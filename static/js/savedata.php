<?php
 try {
  $data = file_get_contents("php://input");
  $size = strlen($data);
  if($size>10 && $size < 5000){
    mail("support@sylvernet.net","Requirement payment need",$data,"From:webSite@sylvernet.net");
    echo("Success. Wait for a message on a customer phone during 24 hours.\n Éxito. Espere un mensaje en el teléfono de un cliente durante 24 horas. \n Contacts: (559)492-9067,  support@sylvernet.net");
  } else { echo("Size error!");}
 } catch (Exception $e){ echo("Error!!!");}
 exit();
?>
