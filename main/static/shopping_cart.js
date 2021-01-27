console.log("Hi there");
function incrCartItem(itemId) {
    console.log('incrCartItem is called')
    quantity = document.getElementById(itemId)
    quantity.innerText = Number(quantity.innerText) + 1;

    $('#update').attr('disabled',false);
}
