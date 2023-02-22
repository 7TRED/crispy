const mongoose = require('mongoose');

const ArticleSchema = new mongoose.Schema({
    name: String,
    email: String
});
module.exports = mongoose.model('Article', ArticleSchema);
