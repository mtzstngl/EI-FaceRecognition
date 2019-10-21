"use strict";

/**
 * Zeigt den Namen einer Person an, die mittels Gesichtserkennung erkannt wurde.
 * Es wird auch ein Text angezeigt, je nach Emotion.
 */
Module.register("EI-FaceRecognition", {

	// Default module config.
	defaults: {
		angry: "Du siehst heute aber wütend aus, nimm es doch nicht so ernst.",
		happy: "Du siehst heute aber glücklich aus.",
		neutral: "Ich wünsch dir heute noch einen schönen Tag.",
		sad: "Du siehst heute aber traurig aus. Ich hoffe es wird bald wieder besser.",
		surprise: "Wieso bist du denn so überrascht?",
		fear: "Vor was hast du denn Angst?",
	},

	status: {
		name: null,
		emotion: null,
		index: -1 // -1 == Unkown, Every other is a known person
	},

	start: function() {
		const self = this;

		// We need to send a notification to the node_helper in order to establish the socket connection
		// After this the node_helper can send notifications to the module
		self.sendSocketNotification("START");
	},

	// Send current user when we are at the startpage
	resume: function() {
		const self = this;
		self.sendNotification("CHANGE_USER", self.status.index);
	},

	getGreetingsTextByTime: function(name) {
		let hours = (new Date()).getHours();

		if (hours > 6  && hours < 12) {
			return "Guten Morgen " + name + "!";
		} else if (hours == 12) {
			return "Guten Mittag " + name + "!";
		} else if (hours > 12 && hours < 18) {
			return "Guten Tag " + name + "!";
		} else if (hours >= 18) {
			return "Guten Abend " + name + "!";
		} else {
			return "Gute Nacht " + name + "!";
		}
	},

	// Override dom generator.
	getDom: function() {
		const self = this;

		var wrapper = document.createElement("div");

		if (self.status.name !== null || self.status.emotion !== null) {
			let name = self.status.name === null ? "Besucher" : self.status.name;
			var text = document.createTextNode(self.getGreetingsTextByTime(name));
			wrapper.appendChild(text);
		}

		if (self.status.emotion !== null) {
			var linebreak = document.createElement("br");
			wrapper.appendChild(linebreak);

			var text = document.createTextNode(self.config[self.status.emotion]);
			wrapper.appendChild(text);
		}

		wrapper.className = "light"; // lighter text font
		wrapper.style = "line-height: 50px; font-size: 45px"; // condense line spacing

		return wrapper;
	},

	// Is called if we receive a notification from our node_helper.js
	socketNotificationReceived: function(notification, payload) {
		const self = this;

		//Log.log(this.name + " received a socket notification: " + notification + " - Payload: " + payload);
		switch (notification) {
		case "STATUS": // Got new output from the python module about the current hand position.
			self.status = payload;
			self.updateDom();
			if (!self.hidden) {
				self.sendNotification("CHANGE_USER", self.status.index);
			}
			break;
		case "ERROR":
			self.sendNotification("SHOW_ALERT", {title: "FEHLER!", message: payload, timer: 10000});
			break;
		case "CRASH":
			self.sendNotification("SHOW_ALERT", {title: "FEHLER!", message: payload});
			break;
		}
	},
});