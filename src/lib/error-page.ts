export function renderErrorPage(): string {
  return `
    <!DOCTYPE html>
    <html lang="en">
      <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>Error</title>
        <style>
          * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
          }
          body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
              'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
              sans-serif;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
          }
          .error-container {
            background: white;
            border-radius: 10px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            padding: 40px;
            max-width: 500px;
            text-align: center;
          }
          .error-code {
            font-size: 72px;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 20px;
          }
          .error-title {
            font-size: 24px;
            font-weight: 600;
            color: #333;
            margin-bottom: 10px;
          }
          .error-message {
            font-size: 16px;
            color: #666;
            margin-bottom: 30px;
            line-height: 1.6;
          }
          .error-button {
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 12px 30px;
            border-radius: 5px;
            text-decoration: none;
            font-weight: 600;
            transition: transform 0.2s, box-shadow 0.2s;
            border: none;
            cursor: pointer;
            font-size: 16px;
          }
          .error-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.4);
          }
        </style>
      </head>
      <body>
        <div class="error-container">
          <div class="error-code">500</div>
          <div class="error-title">Server Error</div>
          <div class="error-message">
            Something went wrong on our end. Please try again later.
          </div>
          <button class="error-button" onclick="location.href='/'">Go Home</button>
        </div>
      </body>
    </html>
  `;
}
