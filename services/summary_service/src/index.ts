const express = require("express");
import dotenv from "dotenv";
import { Application, Request, Response } from "express";
import mongoose, { ConnectOptions } from "mongoose";
const Article = require("./model/ArticleModel");

dotenv.config();
const app: Application = express();
const port: number = 3000;

app.use(express.json());
app.use(express.urlencoded({ extended: false }));

mongoose.connect(process.env.MONGO_URI!, {
	useNewUrlParser: true,
	useUnifiedTopology: true,
} as ConnectOptions);

app.get("/articles", async (req: Request, res: Response) => {
	try {
		// pageSize = 10
		// make this request more efficient
		const page: number = req.query?.page ? parseInt(req.query.page as string) : 1;
		const articles = await Article.find({})
			.sort({ date: -1 })
			.skip((page - 1) * 10)
			.limit(10);
		res.send({
			title: "Hello World",
			articles: articles,
			adass: "adad",
		});
	} catch (e) {
		console.log("as");
		res.send(e);
	}
});

app.post("/article", async (req: Request, res: Response) => {
	try {
		const article = new Article({
			title: req.body.title,
			content: req.body.content,
			date: new Date(req.body.date),
			url: req.body.url,
		});
		await article.save();
		res.send("Article saved!!");
	} catch (e) {
		console.log(e);
	}
});

app.listen(port, () => {
	console.log(`Listening at port ${port}`);
});
