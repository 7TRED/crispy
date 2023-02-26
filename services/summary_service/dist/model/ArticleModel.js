"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const mongoose_1 = require("mongoose");
const ArticleSchema = new mongoose_1.Schema({
    title: { type: String, required: true },
    content: { type: String, requied: true },
    date: { type: Date, requied: true },
    url: { type: String, requied: true }
});
module.exports = (0, mongoose_1.model)('Article', ArticleSchema);
