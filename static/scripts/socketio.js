document.addEventListener('DOMContentLoaded', () => {
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

    socket.on('start-game', data => {
        const role = document.getElementById('role-get').value;
        console.log(role);
        socket.emit('start-game', { 'roomCode': data.roomCode, 'role': role });
        console.log(data);
    })
    history.pushState(null, document.title, location.href);
    window.addEventListener('popstate', function (event) {
        history.pushState(null, document.title, location.href);
    });
    socket.on("test", data => {
        document.getElementById("link-hidden").style.display = "block";
        // document.location.href = '/gamePlayer/' + data.roomCode + '/' + data.role;
    });
});