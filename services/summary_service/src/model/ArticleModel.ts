import { Schema, model } from 'mongoose';

interface IArticle {
    title: String;
    content: String;
    date: Date;
    url: String;
}
const ArticleSchema = new Schema<IArticle>({
    title: { type: String, required: true },
    content: { type: String, requied: true },
    date: { type: Date, requied: true },
    url: { type: String, requied: true }
});
module.exports = model<IArticle>('Article', ArticleSchema);
