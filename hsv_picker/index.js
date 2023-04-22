const express = require('express');

const app = express();

const options = {
    setHeaders: (res, path, stat) => {
        res.set("Access-Control-Allow-Origin", "*")
    }
};

app.use(express.static('public', options));

/**app.get('/' , (req, res) => {
    res.sendFile('index.html', {root: `${__dirname}/website`})
});*/

app.listen(3000, () => {
    console.log("Server is running on port 3000.")
});