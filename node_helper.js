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

	// System is ready to boot
	start: function() {
		const self = this;

		let options = {
			mode: "json",
			scriptPath: "modules/EI-FaceRecognition",
			pythonOptions: ["-u"] // This is needed otherwise we don't receive the output until the process has ended
		};

		const shell = new PythonShell("FaceRecognition.py", options);

		// Received output from python script; send it to the main module.
		shell.on("message", function (message) {
			//console.log("MESSAGE: " + JSON.stringify(message));
			self.sendSocketNotification("STATUS", message);
		});
		shell.on("stderr", function (stderr) {
			console.log("STDERR: " + stderr);
		});
		shell.on("error", function (error) {
			console.log("ERROR: " + error);
		});
		shell.on("close", function () {
			console.log("CLOSE");
		});

		console.log("EI-FaceRecognition node_helper started");
	},

	// System is shutting down
	stop: function() {
		console.log("EI-FaceRecognition node_helper stopped");
	},

	// My module (EI-FaceRecognition.js) has sent a notification
	socketNotificationReceived: function(notification, payload) {
		console.log(this.name + " received a socket notification: " + notification + " - Payload: " + payload);
	},
});