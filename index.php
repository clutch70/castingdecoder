<?php
$config = parse_ini_file('config.ini');

session_start(); // Start the session.

use PHPMailer\PHPMailer\PHPMailer;
use PHPMailer\PHPMailer\SMTP;
use PHPMailer\PHPMailer\Exception;
use League\OAuth2\Client\Provider\GenericProvider;
require 'vendor/autoload.php';

$config = parse_ini_file('config.ini');

$application_id = $config['application_id'];
$directory_id = $config['directory_id'];
$secret_value = $config['secret_value'];

// Initialize the cart if it's not already set
if (!isset($_SESSION['cart'])) {
    $_SESSION['cart'] = array();
}

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

// Function to email cart.
function emailCart($application_id, $directory_id, $secret_value) {
    // OAuth 2.0 settings
    $provider = new GenericProvider([
        'clientId'                => $application_id,
        'clientSecret'            => $secret_value,
        'redirectUri'             => 'http://decode.cusnet.net',
        'urlAuthorize'            => 'https://login.microsoftonline.com/common/oauth2/v2.0/authorize',
        'urlAccessToken'          => "https://login.microsoftonline.com/$directory_id/oauth2/v2.0/token",
        'urlResourceOwnerDetails' => '',
        'scopes'                  => 'https://graph.microsoft.com/Mail.Send'
    ]);

    // Get OAuth 2.0 token
    try {
        $accessToken = $provider->getAccessToken('client_credentials');
    } catch (Exception $e) {
        error_log('Error getting access token: ' . $e->getMessage());
        echo 'Error getting access token: ',  $e->getMessage(), "\n";
        return;
    }

    // PHPMailer setup
    $mail = new PHPMailer(true);

    try {
        // Server settings
        $mail->isSMTP();
        $mail->Host       = 'smtp.office365.com';
        $mail->SMTPAuth   = true;
        $mail->AuthType   = 'XOAUTH2';
        $mail->Username   = 'inventory@custardcore.com';
        $mail->Password   = $accessToken->getToken();
        $mail->SMTPSecure = PHPMailer::ENCRYPTION_STARTTLS;
        $mail->Port       = 587;

        // Recipients
        $mail->setFrom('inventory@custardcore.com', 'Mailer');
        $mail->addAddress('fishbowldevs@custardcore.com', 'Receiver Name'); // Add a recipient

        // Attachments
        // Generate the CSV data
        $csv_data = fopen('php://temp', 'r+');
        fputcsv($csv_data, ['Quantity', 'Part Number', 'Description', 'Cost', 'Price']); // Column headings

        // Output the cart items.
        foreach ($_SESSION['cart'] as $partNumber => $item) {
            fputcsv($csv_data, [$item['quantity'], $partNumber, $item['description'], $item['cost'], $item['price']]);
        }

        rewind($csv_data);
        $csv_data_string = stream_get_contents($csv_data);
        fclose($csv_data);

        $mail->addStringAttachment($csv_data_string, 'current_load.csv');

        // Content
        $mail->isHTML(true); // Set email format to HTML
        $mail->Subject = 'Current Load CSV';
        $mail->Body    = 'Please find attached the current load CSV.';

        $mail->send();
        echo 'Message has been sent';
    } catch (Exception $e) {
        error_log('Error sending email: ' . $e->getMessage());
        echo "Message could not be sent. Mailer Error: {$mail->ErrorInfo}";
    }
}

// Check for email cart action
if(isset($_GET['action']) && $_GET['action'] == 'email') {
    emailCart($application_id, $directory_id, $secret_value);
}



// Check for remove from cart action
if(isset($_POST['remove_from_cart'])) {
    $partNumber = $_POST['part_number'];
    unset($_SESSION['cart'][$partNumber]);
}

// Check for export action
if(isset($_GET['action']) && $_GET['action'] == 'export') {
    exportCart();
}

// Check for clear cart action
if(isset($_POST['clear_cart'])) {
    clearCart();
}

// Check for increase quantity action
if(isset($_POST['increase_quantity'])) {
    $partNumber = $_POST['part_number'];
    $_SESSION['cart'][$partNumber]['quantity'] += 1;
}

// Check for decrease quantity action
if(isset($_POST['decrease_quantity'])) {
    $partNumber = $_POST['part_number'];
    $_SESSION['cart'][$partNumber]['quantity'] -= 1;
    if ($_SESSION['cart'][$partNumber]['quantity'] <= 0) {
        unset($_SESSION['cart'][$partNumber]);
    }
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
        $result_count = is_array($output) ? count($output) : 0;
        if ($output) {
            echo '<p>Number of results: ' . $result_count . '</p>'; // Display the number of results
            foreach ($output as $key => $item) {
                // Check for special values or missing data
                $partNumber = isset($item['PartNumber']) ? $item['PartNumber'] : 'N/A';
                $description = isset($item['Description']) ? $item['Description'] : 'No description available';
                $details = isset($item['Details']) ? $item['Details'] : 'N/A';
                $cost = (isset($item['Cost']) && is_numeric($item['Cost'])) ? $item['Cost'] : '0';
                $price = (isset($item['Price']) && is_numeric($item['Price'])) ? $item['Price'] : '0';
                $hollander = isset($item['Hollander']) ? $item['Hollander'] : 'N/A'; // Handling for Hollander column

                echo '<form action="" method="post">';
                echo '<input type="hidden" name="part_number" value="' . htmlspecialchars($partNumber) . '">';
                echo '<input type="hidden" name="description" value="' . htmlspecialchars($description) . '">';
                echo '<input type="hidden" name="cost" value="' . htmlspecialchars($cost) . '">';
                echo '<input type="hidden" name="price" value="' . htmlspecialchars($price) . '">';
                // Include Hollander data in the form if necessary
                echo '<p>Engine Code - ' . htmlspecialchars($partNumber) . '</p>';
                echo '<p>Description - ' . htmlspecialchars($description) . '</p>';
                echo '<p>Hollander - ' . htmlspecialchars($hollander) . '</p>';
                echo '<p>Details - ' . htmlspecialchars($details) . '</p>';
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
                        <td>
                            <form action="" method="post">
                                <input type="hidden" name="part_number" value="<?php echo htmlspecialchars($partNumber); ?>">
                                <button type="submit" name="increase_quantity">+</button>
                                <?php echo htmlspecialchars($item['quantity']); ?>
                                <button type="submit" name="decrease_quantity">-</button>
                            </form>
                        </td>
                        <td><?php echo htmlspecialchars($partNumber); ?></td>
                        <td><?php echo htmlspecialchars($item['description']); ?></td>
                        <td>
                            <form action="" method="post">
                                <input type="hidden" name="part_number" value="<?php echo htmlspecialchars($partNumber); ?>">
                                <button type="submit" name="remove_from_cart">Remove</button>
                            </form>
                        </td>
                    </tr>
                <?php endforeach; ?>
            <?php else: ?>
                <tr>
                    <td colspan="4">Your cart is empty.</td>
                </tr>
            <?php endif; ?>

        </tbody>
    </table>
    <form action="" method="post">
        <button type="submit" name="clear_cart">Clear Load</button>
    </form>

    <a href="?action=export">Export as CSV</a> <a href="?action=email" style="display: none;">Email To Office</a>
    <form action="send_to_po.php" method="post" id="sendToPoForm">
        <input type="hidden" name="cart_data" id="cartDataInput">
        <input type="hidden" name="po_number" id="poNumberInput">
        <button type="button" id="sendToPoButton">Send To PO</button>
    </form>
</div>
<div class="footer-logo">
        <a href="/">
            <img src="logo.png" alt="Custard Core Logo">
        </a>
    </div>
</body>
</html>
<script>
    var cart = <?php echo json_encode($_SESSION['cart']); ?>;

    document.getElementById('sendToPoButton').addEventListener('click', function() {
        var cartData = JSON.stringify(cart);
        document.getElementById('cartDataInput').value = cartData;

        var poNumber = prompt("Please enter the PO Number:");
        document.getElementById('poNumberInput').value = poNumber;

        document.getElementById('sendToPoForm').submit();
    });
</script>