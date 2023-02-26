"use strict";
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const express = require("express");
const dotenv_1 = __importDefault(require("dotenv"));
const mongoose_1 = __importDefault(require("mongoose"));
const Article = require("./model/ArticleModel");
dotenv_1.default.config();
const app = express();
const port = 3000;
app.use(express.json());
app.use(express.urlencoded({ extended: false }));
mongoose_1.default.connect(process.env.MONGO_URI, {
    useNewUrlParser: true,
    useUnifiedTopology: true,
});
app.get("/", (req, res) => __awaiter(void 0, void 0, void 0, function* () {
    try {
        const articles = yield Article.find({}).orderBy({ date: -1 }).skip(10).limit(10);
        console.log("hellowe");
        res.send({
            title: "Hello World",
            articles: articles,
            adass: "adad",
        });
    }
    catch (e) {
        res.send(e);
    }
}));
app.post("/article", (req, res) => __awaiter(void 0, void 0, void 0, function* () {
    try {
        const article = new Article({
            title: req.body.title,
            content: req.body.content,
            date: new Date(req.body.date),
            url: req.body.url,
        });
        yield article.save();
        res.send("Article saved!!");
    }
    catch (e) {
        console.log(e);
    }
}));
app.listen(port, () => {
    console.log(`Listening at port ${port}`);
});
