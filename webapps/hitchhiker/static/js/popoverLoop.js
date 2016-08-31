// $('.user').each(function() {
// 		var $this = $(this);
// 		$this.popover({
// 			trigger: 'hover',
// 			placement: 'left',
// 			html: true,
// 			content: $this.find('.userInfo').html()  
// 		});
// });
hover = null;

function activeHover() {
    $('.user').each(function() {
        var $this = $(this);
        $this.popover({
            trigger: 'hover',
            placement: 'left',
            html: true,
            content: $this.find('.userInfo').html()  
        });
    });
}

activeHover();
// function hoverWrapper() {
//     console.log("active hover!");
//     hover;
// }
// hoverWrapper();