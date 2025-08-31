const express = require('express');
const cors = require('cors');

const app = express();
const PORT = process.env.PORT || 5000;

app.use(cors());
app.use(express.json());

let count = 0;

app.get('/api/count', (req, res) => {
    res.json({ count });
});

app.post('/api/increment', (req, res) => {
    count += 1;
    res.json({ count });
});

app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});