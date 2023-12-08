<?php
session_start(); // Start the session.

// Function to add to cart.
function addToCart($partNumber, $description, $cost, $price, $quantity) {
    if (isset($_SESSION['cart'][$partNumber])) {
        $_SESSION['cart'][$partNumber]['quantity'] += $quantity;
    } else {
        $_SESSION['cart'][$partNumber] = [
            'description' => $description,
            'cost' => $cost,
            'price' => $price,
            'quantity' => $quantity
        ];
    }
}


// Function to clear the cart
function clearCart() {
    $_SESSION['cart'] = array(); // This will reset the cart to an empty array.
}


// Function to export cart.
function exportCart() {
    header('Content-Type: text/csv');
    header('Content-Disposition: attachment; filename="current_load.csv"');

    $output = fopen('php://output', 'w');
    fputcsv($output, ['Quantity', 'Part Number', 'Description', 'Cost', 'Price']); // Column headings

    // Output the cart items.
    foreach ($_SESSION['cart'] as $partNumber => $item) {
        fputcsv($output, [$item['quantity'], $partNumber, $item['description'], $item['cost'], $item['price']]);
}

    fclose($output);
    exit();
}

// Check for export action
if(isset($_GET['action']) && $_GET['action'] == 'export') {
    exportCart();
}

// Check for clear cart action
if(isset($_POST['clear_cart'])) {
    clearCart();
}


// Check for add to cart action
if(isset($_POST['add_to_cart'])) {
    $partNumber = $_POST['part_number'];
    $description = $_POST['description'];
    $cost = $_POST['cost'];
    $price = $_POST['price'];
    $quantity = $_POST['quantity']; // Retrieve quantity from form
    addToCart($partNumber, $description, $cost, $price, $quantity);
}

?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1"> <!-- For mobile responsiveness -->
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
            <p>Enter the details of the core/Ingresa los detalles.</p>
        </div>
        <form action="" method="post">
            <input type="text" name="search_terms" placeholder="example/ejemplo: 3C3E FORD 2l3e 6.8L" value="<?php echo isset($_POST['search_terms']) ? htmlspecialchars($_POST['search_terms']) : ''; ?>">
            <button type="submit" name="submit">Search</button>
        </form>
    </div>
    <div class="output">
    <?php
    if (isset($_POST['submit'])) {
        $search_terms = escapeshellarg($_POST['search_terms']);
        $command = escapeshellcmd("python3 casting_decoder.py $search_terms");
        $json_output = shell_exec($command);
        $json_output = str_replace('NaN', 'null', $json_output);
        $output = json_decode($json_output, true); // Decodes the JSON output to an associative array
        $result_count = count($output); // Count the number of results
        if ($output) {
            echo '<p>Number of results: ' . $result_count . '</p>'; // Display the number of results
            foreach ($output as $key => $item) {
                // Check for special values or missing data
                $partNumber = isset($item['PartNumber']) ? $item['PartNumber'] : 'N/A';
                $description = isset($item['Description']) ? $item['Description'] : 'No description available';
                $cost = (isset($item['Cost']) && is_numeric($item['Cost'])) ? $item['Cost'] : '0';
                $price = (isset($item['Price']) && is_numeric($item['Price'])) ? $item['Price'] : '0';
                $hollander = isset($item['Hollander']) ? $item['Hollander'] : 'N/A'; // Handling for Hollander column

                echo '<form action="" method="post">';
                echo '<input type="hidden" name="part_number" value="' . htmlspecialchars($partNumber) . '">';
                echo '<input type="hidden" name="description" value="' . htmlspecialchars($description) . '">';
                echo '<input type="hidden" name="cost" value="' . htmlspecialchars($cost) . '">';
                echo '<input type="hidden" name="price" value="' . htmlspecialchars($price) . '">';
                // Include Hollander data in the form if necessary
                echo '<p>' . htmlspecialchars($description) . ' - Hollander: ' . htmlspecialchars($hollander) . '</p>';
                echo '<input type="number" name="quantity" value="1" min="1">';
                echo '<button type="submit" name="add_to_cart">Add to Load</button>';
                echo '</form>';
            }
        } else {
            echo '<p>No results found.</p>';
        }
    }
    ?>
</div>

<!-- Cart Display -->
<div class="cart-container">
    <h2>Current Load</h2>
    <table>
        <thead>
            <tr>
                <th>Quantity</th>
                <th>Part Number</th>
                <th>Description</th>
            </tr>
        </thead>
        <tbody>
            <?php if (!empty($_SESSION['cart'])): ?>
                <?php foreach ($_SESSION['cart'] as $partNumber => $item): ?>
                    <tr>
                        <td><?php echo htmlspecialchars($item['quantity']); ?></td>
                        <td><?php echo htmlspecialchars($partNumber); ?></td>
                        <td><?php echo htmlspecialchars($item['description']); ?></td>
                    </tr>
                <?php endforeach; ?>
            <?php else: ?>
                <tr>
                    <td colspan="3">Your cart is empty.</td>
                </tr>
            <?php endif; ?>
        </tbody>
    </table>
    <form action="" method="post">
        <button type="submit" name="clear_cart">Clear Load</button>
    </form>

    <a href="?action=export">Export as CSV</a>
    <form action="send_to_po.php" method="post" id="sendToPoForm">
        <input type="hidden" name="cart_data" id="cartDataInput">
        <input type="hidden" name="po_number" id="poNumberInput">
        <button type="button" id="sendToPoButton">Send To PO</button>
    </form>
</div>
<div class="footer-logo">
        <a href="http://decode.custardcore.com">
            <img src="logo.png" alt="Custard Core Logo">
        </a>
    </div>
</body>
</html>
<script>
    var cart = <?php echo json_encode($_SESSION['cart']); ?>;
</script>
<script>
document.getElementById('sendToPoButton').addEventListener('click', function() {

    // Get the cart data and convert it to a JSON string

    var cartData = JSON.stringify(cart);  // Replace 'cart' with your cart variable
    document.getElementById('cartDataInput').value = cartData;

    // Show a prompt asking the user for the PO Number
    var poNumber = prompt("Please enter the PO Number:");
    document.getElementById('poNumberInput').value = poNumber;

    // Submit the form
    document.getElementById('sendToPoForm').submit();
});
</script>