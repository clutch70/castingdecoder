<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="style.css">
    <title>Casting Decoder</title>
</head>
<body>
    <header>
        <h1>Custard Core</h1>
    </header>
    <main>
        <section class="form-container">
            <h2>Casting Decoder</h2>
            <p>Enter the casting numbers below to decode the casting. Partial numbers are ok, but are case sensitive.</p>
            <p>Introduce los números de fundición a continuación para descifrar el molde. Los números parciales están bien, pero son sensibles a mayúsculas y minúsculas.</p>
            <form method="post">
                <!-- Add form fields here -->
                <input type="text" name="block" placeholder="Block">
                <input type="text" name="right_head" placeholder="Right Head">
                <input type="text" name="left_head" placeholder="Left Head">
                <input type="text" name="crank" placeholder="Crank">
                <input type="text" name="hollander" placeholder="Hollander">
                <button type="submit">Submit</button>
            </form>
            <?php
                // Check if form is submitted
                if ($_SERVER["REQUEST_METHOD"] == "POST") {
                    // Collect input from the form and build the command
                    $args = [];
                    if (!empty($_POST['block'])) {
                        $args[] = '--block ' . escapeshellarg($_POST['block']);
                    }
                    if (!empty($_POST['right_head'])) {
                        $args[] = '--right_head ' . escapeshellarg($_POST['right_head']);
                    }
                    if (!empty($_POST['left_head'])) {
                        $args[] = '--left_head ' . escapeshellarg($_POST['left_head']);
                    }
                    if (!empty($_POST['crank'])) {
                        $args[] = '--crank ' . escapeshellarg($_POST['crank']);
                    }
                    if (!empty($_POST['hollander'])) {
                        $args[] = '--hollander ' . escapeshellarg($_POST['hollander']);
                    }

                    $command = 'python3 casting_decoder.py ' . implode(' ', $args);
                    $output = shell_exec($command);

                    // Display the output
                    echo "<div class='output'><pre>$output</pre></div>";

                }
            ?>
        </section>
    </main>
</body>
</html>

