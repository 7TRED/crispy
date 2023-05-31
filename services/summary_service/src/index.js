const express = require("express");
const mongoose = require("mongoose");
const dotenv = require("dotenv");
const summaryRouter = require("./routes/summary");

dotenv.config();
const app = express();

app.set("view engine", "ejs");

const COMPLETE_MONGO_URI = process.env.MONGO_URI + process.env.MONGO_DB;
console.log(COMPLETE_MONGO_URI);
// Connect to MongoDB
mongoose.connect(COMPLETE_MONGO_URI, {
	useNewUrlParser: true,
	useUnifiedTopology: true,
});

app.use(express.static("public"));

app.use("/", summaryRouter);

const PORT = process.env.PORT || 3000;

app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
