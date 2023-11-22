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
    echo "<pre>$output</pre>";
}
?>