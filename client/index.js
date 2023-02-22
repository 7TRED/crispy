const express = require('express');
require('dotenv').config();
const mongoose = require('mongoose');
const Article = require('./model/ArticleModel');
const app = express();
const port = 3000;
console.log(process.env.URI);

app.use(express.json());
app.use(express.urlencoded({ extended: false }));

// app.get('/', (req, res) => {
//     res.send('Hello World!!');
// });
mongoose.connect(process.env.URI, { useNewUrlParser: true, useUnifiedTopology: true });

app.get('/', async (req, res) => {
    try {
        const articles = await Article.find({});
        res.send(articles);
    } catch (e) {
        res.send(e);
    }
});
app.post('/article', async (req, res) => {
    try {
        const articles = new Article({
            name: req.body.name,
            email: req.body.email
        });
        await articles.save();
        res.send('article saved!!');
    } catch (e) {
        console.log(e);
    }
});

app.listen(port, () => {
    console.log(`listning at port ${port}`);
});
