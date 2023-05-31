const mongoose = require("mongoose");

const SummarySchema = new mongoose.Schema(
	{
		article_id: { type: String, required: true },
		summary: { type: String, required: true },
		date: { type: Date, required: true },
		url: { type: String, required: true },
		title: { type: String, required: true },
		audio: { type: mongoose.Schema.Types.ObjectId, ref: "Audio" },
	},
	{
		timestamps: true,
		collection: "summaries",
	},
);

module.exports = mongoose.model("Summary", SummarySchema);
