<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>CCS - Engine Decoder</title>
    <link rel="stylesheet" href="style.css"> <!-- Link to external CSS file -->
</head>
<body>
    <header>
        <h1>Custard Core Engine Decoder</h1>
    </header>
    <div class="form-container">
        <div class="instructions">
            <h2>Instructions:</h2>
            <p>Enter search terms to find in the CSV description field.</p>
        </div>
        <form action="" method="post">
            <input type="text" name="search_terms" placeholder="Enter terms...">
            <button type="submit" name="submit">Search</button>
        </form>
    </div>
    <div class="output">
        <?php
        if (isset($_POST['submit'])) {
            $search_terms = escapeshellarg($_POST['search_terms']);
            // Call the Python script with the search terms
            $command = escapeshellcmd("python engine_lookup.py $search_terms");
            $output = shell_exec($command);
            echo htmlspecialchars($output);
        }
        ?>
    </div>
</body>
</html>
