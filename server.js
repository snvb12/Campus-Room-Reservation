
const express = require('express');
const cors = require('cors');
const app = express();
const PORT = 3000;

app.use(cors());
app.use(express.json());

let reservations = [];

app.post('/reserve', (req, res) => {
    const data = req.body;

    if (!data.name || !data.room || !data.date || !data.time) {
        return res.json({ error: 'Missing fields' });
    }

    reservations.push(data);

    res.json({ message: 'Saved', data: data });
});

app.get('/reservations', (req, res) => {
    res.json(reservations);
});

app.listen(PORT, () => {
    console.log('Simple backend running on port ' + PORT);
});
