$(document).ready(function () {
    $("input[type='radio']").on("change", function(){
        var x;
        if (confirm("YOU ARE ABOUT TO RATE THIS USER " + this.value + " STARS") == true) {
            x = "User has been rated. Thank you for your response.";
        } else {
            x = "Rate this user above.";
        }
        document.getElementById("demo").innerHTML = x;

        ratingGiven = this.value;

        var buyerEmail = document.getElementById("buyerEmail").innerHTML;
        var sellerEmail = document.getElementById("sellerEmail").innerHTML;
        var bookName = document.getElementById("bookName").innerHTML;
        var author= document.getElementById("author").innerHTML;
        var price = document.getElementById("price").innerHTML;
        var condition = document.getElementById("condition").innerHTML;

        urlLink = "/rate/" + buyerEmail + "/"+ sellerEmail + "/"+ bookName + "/" + author + "/" + price + "/"+ condition;

        alert("hello");

        console.log("hello");
        $.ajax({
        type: "GET",
        url: urlLink,
        data:{"rate":ratingGiven},
        //success: function(){ window.location.href="/rate"; } ,
        });

    });
});
