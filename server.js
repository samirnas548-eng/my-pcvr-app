const WebSocket = require('ws');
const hid = require('node-hid');

const wss = new WebSocket.Server({ port: 8080 });
console.log("🎮 HACKED JOY-CON VR SERVER RUNNING ON PORT 8080 🎮");

wss.on('connection', (ws) => {
    console.log("🔗 iPhone VR Headset Connected over Wi-Fi!");

    const devices = hid.devices();
    const joycons = devices.filter(d => d.vendorId === 1406);

    if (joycons.length === 0) {
        console.log("❌ No Joy-Cons found! Make sure they are paired to Windows via Bluetooth.");
        return;
    }

    joycons.forEach((deviceInfo) => {
        try {
            const joycon = new hid.HID(deviceInfo.path);
            const handType = deviceInfo.productId === 0x2006 ? 'left' : 'right';
            console.log(`✅ Hacked and Connected to ${handType} Switch 2 Joy-Con!`);

            const enableIMUPacket = [0x01, 0x00, 0x01, 0x40, 0x40, 0x00, 0x01, 0x40, 0x40, 0x03, 0x30];
            joycon.write(enableIMUPacket);

            joycon.on('data', (rawPacket) => {
                if (rawPacket[0] === 0x30) {
                    let accelX = rawPacket.readInt16LE(13);
                    let accelY = rawPacket.readInt16LE(15);
                    let accelZ = rawPacket.readInt16LE(17);

                    let pitch = Math.atan2(accelY, accelZ) * (180 / Math.PI);
                    let yaw = Math.atan2(-accelX, Math.sqrt(accelY * accelY + accelZ * accelZ)) * (180 / Math.PI);
                    let roll = 0;

                    const vrPacket = {
                        type: 'controller_update',
                        hand: handType,
                        pitch: pitch,
                        yaw: yaw,
                        roll: roll,
                        triggerPressed: (rawPacket[2] & 0x80) !== 0
                    };

                    if (ws.readyState === WebSocket.OPEN) {
                        ws.send(JSON.stringify(vrPacket));
                    }
                }
            });

        } catch (err) {
            console.log("⚠️ Error hooking into Joy-Con stream:", err.message);
        }
    });
});
