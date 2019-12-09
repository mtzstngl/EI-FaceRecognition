var NodeHelper = require("node_helper");
const {PythonShell} = require("python-shell");

/**
 * Ruft mittels PythonShell FaceRecognition.py auf, was die Gesichtserkennung durchführt.
 * Die Ergebnisse der Gesichtserkennung, werden mittels JSON ausgetauscht.
 * JSON Object:
 * {
 *     "name":  None,
 *     "emotion": None
 * }
 */
module.exports = NodeHelper.create({

	shell: null,
	scanning: false,

	// System is ready to boot
	start: function() {
		const self = this;

		let options = {
			mode: "json",
			//pythonPath: "/home/smartmirror/MagicMirror/modules/EI-FaceRecognition/Gesichtserkennung/venv/bin/python3", // production version
			//scriptPath: "modules/EI-FaceRecognition/Gesichtserkennung", // production version
			scriptPath: "modules/EI-FaceRecognition",
			pythonOptions: ["-u"] // This is needed otherwise we don't receive the output until the process has ended
		};

		//const shell = new PythonShell("Gesichtserkennung.py", options); // production version
		self.shell = new PythonShell("FaceRecognition.py", options);

		// Received output from python script; send it to the main module.
		self.shell.on("message", function (message) {
			//console.log("MESSAGE: " + JSON.stringify(message));
			if (self.scanning) {
				self.sendSocketNotification("MEDICINE", message);
			}
			else {
				self.sendSocketNotification("STATUS", message);
			}
		});
		self.shell.on("stderr", function (stderr) {
			console.log("STDERR: " + stderr);
			self.sendSocketNotification("ERROR", stderr);
		});
		self.shell.on("error", function (error) {
			console.log("ERROR: " + error);
			self.sendSocketNotification("CRASH", "Die Gesichtserkennung wurde unerwartet beendet! Bitte PC neustarten!");
		});
		self.shell.on("close", function () {
			console.log("CLOSE");
			self.sendSocketNotification("CRASH", "Die Gesichtserkennung wurde unerwartet beendet! Bitte PC neustarten!");
		});

		console.log("EI-FaceRecognition node_helper started");
	},

	// System is shutting down
	stop: function() {
		console.log("EI-FaceRecognition node_helper stopped");
	},

	// My module (EI-FaceRecognition.js) has sent a notification
	socketNotificationReceived: function(notification, payload) {
		const self = this;
		console.log(this.name + " received a socket notification: " + notification + " - Payload: " + payload);

		switch(notification) {
			case "startscanning":
				self.scanning = true;
				self.shell.send("startscanning");
				break;
			case "stopscanning":
				self.scanning = false;
				break;
		}
	},
});