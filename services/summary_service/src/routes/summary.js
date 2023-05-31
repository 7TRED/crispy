const express = require("express");
const Summary = require("../model/Summary");

const router = express.Router();

router.get("/", async (req, res) => {
	const perPage = 10;
	const page = req.query.page || 1;

	try {
		const summaries = await Summary.find({})
			.skip(perPage * (page - 1))
			.limit(perPage)
			.sort({ date: "desc" })
			.exec();

		const count = await Summary.countDocuments();

		res.render("summary", {
			news: summaries,
			page: parseInt(page),
			pages: Math.ceil(count / perPage),
		});
	} catch (err) {
		console.error(err);
		res.render("error/500");
	}
});

module.exports = router;
