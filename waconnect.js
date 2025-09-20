const { default: makeWASocket, useMultiFileAuthState, DisconnectReason } = require("@whiskeysockets/baileys");
const fs = require("fs");
const WebSocket = require("ws");

async function connectWA() {
    const { state, saveCreds } = await useMultiFileAuthState("auth");

const P = require("pino"); // tambahkan ini di atas
const serv = makeWASocket({
    auth: state,
    logger: P({ level: 'silent' }), // ini wajib bro!
    printQRInTerminal: true,
});


    serv.ev.on("connection.update", async (update) => {
    const { connection, lastDisconnect, qr } = update;

    if (qr) {
    const QRCode = require("qrcode");
    QRCode.toFile("qr.png", qr, function (err) {
        if (err) throw err;
        console.log("🖼️ QR Code disimpan ke qr.png");
    });
    }

        if (connection === "close") {
            const reason = lastDisconnect?.error?.output?.statusCode;
            console.log(`--------- 🔄 Koneksi terputus, kode: ${reason} (${DisconnectReason[reason] || "Unknown"}) ---------`);
            
            if (reason === DisconnectReason.loggedOut) {
                console.log("--------- ❌ Logout! Hapus folder `auth` dan scan ulang QR! ---------");
                process.exit(1);
            } else {
                console.log("--------- 🔄 Reconnecting... ---------");
                setTimeout(connectWA, 5000);
            }
        } else if (connection === "open") {
            console.log(`--------- ✅ Sesi siap! Akun: ${serv.user.id} ---------`);
        }
    });

    serv.ev.on("creds.update", saveCreds);

    return serv;
}

async function startServer() {
    const serv = await connectWA();
    const wss = new WebSocket.Server({ port: 3000 });

    wss.on("connection", (ws) => {
        console.log("📡 Python terhubung ke WebSocket!");

        ws.on("message", async (message) => {
            try {
                const data = JSON.parse(message);
                console.log("📩📡 Perintah Python diterima:", data);

                if (!data.nomor) {
                    ws.send(JSON.stringify({ status: "error", message: "Nomor tidak ditemukan!" }));
                    return;
                }

                let nomor = data.nomor.replace(/\D/g, "") + "@s.whatsapp.net";
                let tipe = data.tipe?.toUpperCase();

                if (tipe === "TEXT") {
                    await serv.sendMessage(nomor, { text: data.pesan });
                    ws.send(JSON.stringify({ status: "success", message: "Pesan teks terkirim!" }));
                } else if (tipe === "FOTO") {
                    if (!fs.existsSync(data.pesan)) {
                        ws.send(JSON.stringify({ status: "error", message: "File Foto tidak ditemukan!" }));
                        return;
                    }
                    const image = fs.readFileSync(data.pesan);
                    await serv.sendMessage(nomor, { image, caption: data.caption || "" });
                    ws.send(JSON.stringify({ status: "success", message: "Foto terkirim!" }));
                } else {
                    ws.send(JSON.stringify({ status: "error", message: "Jenis pesan tidak dikenal!" }));
                }
            } catch (err) {
                console.error("❌ Error saat memproses pesan:", err);
                ws.send(JSON.stringify({ status: "error", message: "Gagal mengirim pesan!" }));
            }
        });
    });

    serv.ev.on("messages.upsert", async (m) => {
        const msg = m.messages[0];
        if (!msg.message || !msg.key.remoteJid) return;

        let pesan = msg.message.conversation || msg.message.extendedTextMessage?.text;
        let pengirim = msg.key.remoteJid.replace("@s.whatsapp.net", "");

        console.log(`📩 Pesan dari ${pengirim}: ${pesan}`);

        const clients = [...wss.clients].filter(client => client.readyState === WebSocket.OPEN);

        const sendToAllClients = (command) => {
            console.log(`🔄 Mengirim "${command}" ke ${clients.length} client`);
            clients.forEach(client => client.send(JSON.stringify({perintah: command})));
        };

        if (pesan === ".alert") {
            sendToAllClients("alert");  
            await serv.sendMessage(msg.key.remoteJid, { text: "✅ Mengaktifkan alert!" });
        } else if (pesan === ".unalert") {
            sendToAllClients("unalert");
            await serv.sendMessage(msg.key.remoteJid, { text: "✅ Menonaktifkan alert!" });
        } else if (pesan === ".logoff") {
            sendToAllClients("logoff");
            await serv.sendMessage(msg.key.remoteJid, { text: "✅ Melakukan LogOff Komputer" });
        }
    });

    console.log("🚀 WebSocket server berjalan di port 3000!");
}

startServer();
