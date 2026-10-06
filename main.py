<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Анализатор Patricia 5.1</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #1e1e1e;
            color: #fff;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 10px;
            margin: 0;
        }
        h1 { margin: 10px 0; color: #f0d9b5; font-size: 22px; text-align: center; }
        .board-container {
            width: 100%;
            max-width: 360px;
            aspect-ratio: 1;
            display: grid;
            grid-template-columns: repeat(8, 1fr);
            grid-template-rows: repeat(8, 1fr);
            border: 4px solid #333;
            border-radius: 4px;
            margin-bottom: 15px;
        }
        .square {
            display: flex;
            justify-content: center;
            align-items: center;
            position: relative;
            user-select: none;
            -webkit-user-select: none;
        }
        .white-sq { background-color: #f0d9b5; }
        .black-sq { background-color: #b58863; }
        .square img {
            width: 90%;
            height: 90%;
            cursor: pointer;
        }
        .selected { background-color: #7bab72 !important; }
        .controls { width: 100%; max-width: 360px; display: flex; gap: 10px; margin-bottom: 15px; }
        button {
            flex: 1; padding: 12px; font-size: 16px; font-weight: bold;
            background-color: #b58863; color: white; border: none; border-radius: 4px; cursor: pointer;
        }
        button:active { background-color: #8a623e; }
        #output {
            width: 100%; max-width: 340px; background: #2a2a2a; padding: 10px;
            border-radius: 4px; border-left: 5px solid #b58863; font-size: 15px; min-height: 80px;
        }
        .status-line { font-weight: bold; margin-bottom: 5px; }
        .engine-move { color: #4caf50; font-size: 18px; font-weight: bold; }
    </style>
</head>
<body>

    <h1>Анализатор Patricia 5.1</h1>
    
    <!-- Шахматная доска -->
    <div id="board" class="board-container"></div>

    <!-- Кнопки управления -->
    <div class="controls">
        <button id="clearBtn">Сброс</button>
        <button id="analyzeBtn">Анализ Patricia</button>
    </div>

    <!-- Вывод результатов -->
    <div id="output">
        <div class="status-line" id="statusText">Нажмите на фигуру, а затем на поле, чтобы сделать ход.</div>
        <div id="resultText"></div>
    </div>

    <script src="https://cloudflare.com"></script>
    <script>
        const SERVER_URL = "https://onrender.com";
        var game = new Chess();
        var selectedSquare = null;

        const pieceImages = {
            'p': 'https://chessboardjs.com',
            'r': 'https://chessboardjs.com',
            'n': 'https://chessboardjs.com',
            'b': 'https://chessboardjs.com',
            'q': 'https://chessboardjs.com',
            'k': 'https://chessboardjs.com',
            'P': 'https://chessboardjs.com',
            'R': 'https://chessboardjs.com',
            'N': 'https://chessboardjs.com',
            'B': 'https://chessboardjs.com',
            'Q': 'https://chessboardjs.com',
            'K': 'https://chessboardjs.com'
        };

        function drawBoard() {
            const boardDiv = document.getElementById('board');
            boardDiv.innerHTML = '';
            
            // Отрисовка от 8-й горизонтали к 1-й (взгляд за белых)
            for (let r = 0; r < 8; r++) {
                for (let c = 0; c < 8; c++) {
                    const squareId = String.fromCharCode(97 + c) + (8 - r);
                    const square = document.createElement('div');
                    square.classList.add('square');
                    square.classList.add((r + c) % 2 === 0 ? 'white-sq' : 'black-sq');
                    square.dataset.id = squareId;

                    if (selectedSquare === squareId) {
                        square.classList.add('selected');
                    }

                    const piece = game.get(squareId);
                    if (piece) {
                        const img = document.createElement('img');
                        // Используем тип фигуры (верхний регистр для белых, нижний для черных)
                        const code = piece.color === 'w' ? piece.type.toUpperCase() : piece.type;
                        img.src = pieceImages[code];
                        square.appendChild(img);
                    }

                    square.addEventListener('click', () => handleSquareClick(squareId));
                    boardDiv.appendChild(square);
                }
            }
        }

        function handleSquareClick(squareId) {
            if (selectedSquare === null) {
                const piece = game.get(squareId);
                if (piece) {
                    selectedSquare = squareId;
                    drawBoard();
                }
            } else {
                var move = game.move({
                    from: selectedSquare,
                    to: squareId,
                    promotion: 'q'
                });

                selectedSquare = null;
                drawBoard();

                if (move !== null) {
                    document.getElementById('statusText').innerText = "Ход сделан. Нажмите «Анализ».";
                }
            }
        }

        document.getElementById('clearBtn').addEventListener('click', function() {
            game.reset();
            selectedSquare = null;
            drawBoard();
            document.getElementById('statusText').innerText = "Доска сброшена. Сделайте ход.";
            document.getElementById('resultText').innerHTML = "";
        });

        document.getElementById('analyzeBtn').addEventListener('click', async function() {
            const currentFen = game.fen();
            document.getElementById('statusText').innerText = "Patricia думает...";
            document.getElementById('resultText').innerHTML = "Отправка запроса на сервер...";

            try {
                const response = await fetch(`${SERVER_URL}/analyze`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ fen: currentFen, time_limit: 1.5 })
                });

                if (!response.ok) throw new Error("Ошибка сервера");
                const data = await response.json();
                
                document.getElementById('statusText').innerText = "Анализ завершен:";
                document.getElementById('resultText').innerHTML = `
                    <div>Лучший ход: <span class="engine-move">${data.best_move}</span></div>
                    <div>Оценка позиции: <b>${data.score > 0 ? '+' : ''}${data.score}</b></div>
                    <div>Глубина: ${data.depth} полуходов</div>
                `;
            } catch (error) {
                document.getElementById('statusText').innerText = "Ошибка!";
                document.getElementById('resultText').innerText = "Сервер просыпается. Подождите 30 секунд и нажмите кнопку снова.";
            }
        });

        // Первый запуск
        drawBoard();
    </script>
</body>
</html>
