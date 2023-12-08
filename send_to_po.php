<?php
$cart_data = $_POST['cart_data'];
$po_number = $_POST['po_number'];

// Call the Python script with the cart data and the PO Number as arguments
$command = escapeshellcmd("python3 add_po_item.py $po_number $cart_data");
echo $command;
$output = shell_exec($command);
echo $output;

// Handle the output...
?>