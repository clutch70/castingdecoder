<?php
session_start(); // Start the session.

// Function to add to cart.
function addToCart($partNumber, $description, $cost, $price) {
    $_SESSION['cart'][$partNumber] = [
        'description' => $description,
        'cost' => $cost,
        'price' => $price
    ];
}

// Function to export cart.
function exportCart() {
    header('Content-Type: text/csv');
    header('Content-Disposition: attachment; filename="cart.csv"');

    $output = fopen('php://output', 'w');
    fputcsv($output, ['Part Number', 'Description', 'Cost', 'Price']); // Column headings

    // Output the cart items.
    foreach ($_SESSION['cart'] as $partNumber => $item) {
        fputcsv($output, [$partNumber, $item['description'], $item['cost'], $item['price']]);
    }
    fclose($output);
    exit();
}

// Check for export action
if(isset($_GET['action']) && $_GET['action'] == 'export') {
    exportCart();
}

// Check for add to cart action
if(isset($_POST['add_to_cart'])) {
    $partNumber = $_POST['part_number'];
    $description = $_POST['description']; // You'll need to get these details from your form or from the CSV.
    $cost = $_POST['cost'];
    $price = $_POST['price'];
    addToCart($partNumber, $description, $cost, $price);
}
?>

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
        $command = escapeshellcmd("python3 casting_decoder.py $search_terms");
        $output = shell_exec($command);
        $results = json_decode($output, true);

        if ($results) {
            echo '<table>';
            echo '<tr><th>Part Number</th><th>Description</th><th>Cost</th><th>Price</th><th>Action</th></tr>';
            foreach ($results as $partNumber => $details) {
                echo '<tr>';
                echo '<td>' . htmlspecialchars($partNumber) . '</td>';
                echo '<td>' . htmlspecialchars($details['description']) . '</td>';
                echo '<td>' . htmlspecialchars($details['cost']) . '</td>';
                echo '<td>' . htmlspecialchars($details['price']) . '</td>';
                echo '<td><form method="post"><input type="hidden" name="part_number" value="' . htmlspecialchars($partNumber) . '">';
                foreach ($details as $key => $value) {
                    echo '<input type="hidden" name="' . $key . '" value="' . htmlspecialchars($value) . '">';
                }
                echo '<button type="submit" name="add_to_cart">Add to Cart</button></form></td>';
                echo '</tr>';
            }
            echo '</table>';
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
                <th>Part Number</th>
                <th>Description</th>
                <th>Cost</th>
                <th>Price</th>
            </tr>
        </thead>
        <tbody>
            <?php if (!empty($_SESSION['cart'])): ?>
                <?php foreach ($_SESSION['cart'] as $partNumber => $item): ?>
                    <tr>
                        <td><?php echo htmlspecialchars($partNumber); ?></td>
                        <td><?php echo htmlspecialchars($item['description']); ?></td>
                        <td><?php echo htmlspecialchars($item['cost']); ?></td>
                        <td><?php echo htmlspecialchars($item['price']); ?></td>
                    </tr>
                <?php endforeach; ?>
            <?php else: ?>
                <tr>
                    <td colspan="4">Your cart is empty.</td>
                </tr>
            <?php endif; ?>
        </tbody>
    </table>
    <a href="?action=export">Export as CSV</a>
</div>
</body>
</html>
