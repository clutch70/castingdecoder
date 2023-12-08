<?php
$cart_data = $_POST['cart_data'];
$po_number = $_POST['po_number'];

// Escape the arguments
$cart_data_escaped = escapeshellarg($cart_data);
$po_number_escaped = escapeshellarg($po_number);

// Call the Python script with the cart data and the PO Number as arguments
$command = "python3 add_po_item.py $po_number_escaped $cart_data_escaped";
$output = shell_exec($command);

// Clear the cart
$_SESSION['cart'] = [];

// Redirect back to index.php
header('Location: index.php');
exit;
?>