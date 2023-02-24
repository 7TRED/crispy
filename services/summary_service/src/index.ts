const express = require('express');
import dotenv from 'dotenv';
import { Application, Request, Response } from 'express';
import mongoose, { ConnectOptions } from 'mongoose';
const { Article } = require('./model/ArticleModel');

dotenv.config();
const app: Application = express();
const port: number = 3000;

app.use(express.json());
app.use(express.urlencoded({ extended: false }));

mongoose.connect(process.env.MONGO_URI!, { useNewUrlParser: true, useUnifiedTopology: true } as ConnectOptions);

app.get('/', async (_req: Request, res: Response) => {
    try {
        const articles = await Article.find({});
        res.send(articles);
    } catch (e) {
        res.send(e);
    }
});

app.post('/article', async (req: Request, res: Response) => {
    try {
        const article = new Article({
            title:req.body.title,
            content:req.body.content,
            date:Date.parse(req.body.date),
            url:req.body.url,
        });
        await article.save();
        res.send('Article saved!!');
    } catch (e) {
        console.log(e);
    }
});

app.listen(port, () => {
    console.log(`Listening at port ${port}`);
});
