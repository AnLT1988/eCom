console.log("Hi there");
function incrCartItem(itemId) {
    console.log('incrCartItem is called')
    quantity = document.getElementById(itemId)
    let new_quantity = Number(quantity.attributes.value.value) + 1
    console.log(new_quantity)
    quantity.setAttribute('value', new_quantity)

    $('#update').attr('disabled',false);
}
