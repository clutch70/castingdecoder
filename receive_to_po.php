<?php
// Check if the request method is POST
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    // Get the cart data and PO number from the POST request
    $cart_data = $_POST['cart_data'];
    $po_number = $_POST['po_number'];

    // Convert the cart data from a JSON string to a PHP array
    $cart_data = json_decode($cart_data, true);

    // Call the receive_to_po.py script with the cart data and PO number as command line arguments
    $command = escapeshellcmd("python3 receive_to_po.py '$po_number' '" . json_encode($cart_data) . "'");
    $output = shell_exec($command);

    // Print the output of the script
    echo $output;
}