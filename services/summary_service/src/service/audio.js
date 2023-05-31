const sdk = require("microsoft-cognitiveservices-speech-sdk");

module.exports = class AudioSynthesizer {
	speechConfig = sdk.SpeechConfig.fromSubscription(
		process.env.SPEECH_KEY,
		process.env.SPEECH_REGION,
	);

	constructor(speechConfig) {
		this.speechConfig.speechSynthesisVoiceName = speechConfig.speechSynthesisVoiceName;
	}

	async synthesizeText(text, cb) {
		let speechSynthesizer = new sdk.SpeechSynthesizer(this.speechConfig);
		speechSynthesizer.speakTextAsync(
			text,
			(result) => {
				if (result.reason === sdk.ResultReason.SynthesizingAudioCompleted) {
					console.log("synthesis finished.");
					cb && cb(result);
				} else {
					console.error(
						"Speech synthesis canceled, " +
							result.errorDetails +
							"\nDid you set the speech resource key and region values?",
					);
				}
				speechSynthesizer.close();
			},
			(err) => {
				console.trace("err - " + err);
			},
		);
	}
};
