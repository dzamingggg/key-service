const express = require("express");
const app = express();

app.get("/wake", (req, res) => {
  res.send("Server awake!");
});

// Các route khác...
app.listen(process.env.PORT || 3000, () => {
  console.log("Server running");
});
