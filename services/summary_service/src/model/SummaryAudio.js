const { Schema, model } = require("mongoose");

const SummaryAudioSchema = new Schema({
	summary_id: { type: String, required: true },
	audio: { type: Buffer, required: true },
});

module.exports = model("SummaryAudio", SummaryAudioSchema);
