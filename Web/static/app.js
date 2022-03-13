
var username = '';
while (!username) {
	username = prompt('Put Your Name : ')
	if ( username ) {
		if (!username.trim()) username = '';
	}
}
var Code = null

const image = document.getElementById("image")
const socket = new ReconnectingWebSocket( "ws://" + window.location.host + "/ws")
const WatcherList = document.getElementById('watcher-list')
const N_Watcher = document.getElementById('body-detail-number')

socket.onopen = (e) => {
	socket.send(JSON.stringify({username}))
	console.log(e)
}

socket.onmessage = (e) => {
	let data  = JSON.parse(e.data)

	if (data.img) {
		image.src = 'data:image/jpg;base64,' + data.img;
	}

	if (data.MyId) {
		Code = data.data.Id;
		document.getElementById("Username-Space").innerText = data.data.name;
		data.watchers.forEach( wtr => AddWacther(wtr) ) 
	}

	if (data.NewUser) {
		if (data.User.Id === Code) return;
		AddWacther(data.User);
	}


	if (data.UserDisconnect) {
		let User = document.getElementById(data.Id);
		User.classList.add('offline');
		for ( onlineElement of User.getElementsByClassName('watcher-status') ) {
			onlineElement.classList.remove('online');
			NWatcher();
			setTimeout( () => {
				User.remove();
			}, 6000)
		}
	}
}


socket.onclose = (e) => {
	console.log(e)
}

function AddWacther(Watcher) {

		let {name , Id} = Watcher;

		if (Id === Code || !Code) return;

		if ( !document.getElementById(Id) ) {
			let NewUser = document.createElement('div')
			NewUser.setAttribute('class', 'watcher')
			NewUser.setAttribute('id', Id)
			NewUser.innerHTML = `
				<p>${name}</p>
				<div class="watcher-status online"></div>
			`
			WatcherList.appendChild(NewUser);
			NWatcher(add=true);
	}
}

function NWatcher(add = false) {
	let currentNumber = Number(N_Watcher.innerText);
	N_Watcher.innerText = add ? currentNumber + 1 : currentNumber - 1
}


// l = [1,2,3,4]
// name = "dan1"
// for (let i of name) {
// 	try{
// 		Number(i)
// 		throw Error('Invalid name')
// 		break;
// 	} catch {

// 	}
// }

// 	// if (l.includes( i )) throw Error('Invalid name')
