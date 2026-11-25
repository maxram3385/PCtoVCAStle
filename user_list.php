<?php
 //Connect to Database  
 $hostname = "localhost";
 $username = "ecpi_user";
 $password = "Password1";
 $dbname = "sdc310_wk3gp";
 $conn = mysqli_connect($hostname, $username, $password, $dbname);
     
 //Query for all users
 $query = "SELECT * FROM userinfo";
 $result = mysqli_query($conn, $query);
?>

<style>
 table {
 border-spacing: 5px;
    }
 table, th, td {
 border: 1px solid black;
 border-collapse: collapse;
    }
 th, td {
 padding: 15px;
 text-align: center;
    }
 th {
 background-color:lightskyblue;
    }
 tr:nth-child(even) {
 background-color:whitesmoke;
    }
 tr:nth-child(odd) {
 background-color:lightgray;
    }
</style>
<html>
 <head>
 <title>Week3 GP1 - Max Ramos</title>
 </head>

 <body>
 <h2>Current Users:</h2>
 <table>
 <tr style="font-size:large;">
 <th>User #</th>
 <th>First Name</th>
 <th>Last Name</th>
 <th>E-Mail</th>
 <th>Favorite Number</th>
 </tr>
 <?php while($row = mysqli_fetch_array($result)):;?>
 <tr>
 <td><?php echo $row["UserNo"];?></td>
 <td><?php echo $row["FirstName"];?></td>
 <td><?php echo $row["LastName"];?></td>
 <td><?php echo $row["EMail"];?></td>
 <td><?php echo $row["FavoriteNum"];?></td>
 </tr>
 <?php endwhile;?>
 </table>
 </body>
</html>
