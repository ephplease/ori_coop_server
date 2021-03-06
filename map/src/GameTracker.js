import React from 'react';
//import registerServiceWorker from './registerServiceWorker';
import {Map, Tooltip, TileLayer, Marker} from 'react-leaflet';
import {Checkbox, CheckboxGroup} from 'react-checkbox-group';
import {Radio, RadioGroup} from 'react-radio-group';
import Leaflet from 'leaflet';
import {distance, picks_by_type, PickupMarkersList, pickup_icons, getMapCrs, presets} from './shared_map.js';
import Select from 'react-select';
import 'react-select/dist/react-select.css';
import {Button, Collapse} from 'reactstrap';

const paths = Object.keys(presets);
const game_id = document.getElementsByClassName("game-id")[0].id;

const EMPTY_PLAYER = {seed: {}, pos: [0,0], seen:[], flags: ["show_marker", "hide_found", "hide_unreachable"], areas: []}

function parse_seed(raw) {
	let out = {}
	let lines = raw.split("\n")
    for (let i = 0, len = lines.length; i < len; i++) {
    	let line = lines[i].split(":")
    	out[parseInt(line[0])] = line[1]
	}
	return out
};

function player_icons(id)  {
	id = parseInt(id);
	let img = 	'../sprites/ori-white.png';
	if (id === 1)  img = '../sprites/ori-blue.png';
	else if (id === 2)  img = '../sprites/ori-red.png';
	else if (id === 3)  img = '../sprites/ori-green.png';
	else if (id === 4)  img = '../sprites/ori-purple.png';
	else if (id === 5)  img = '../sprites/ori-yellow.png';
	else if (id === 6)  img = '../sprites/ori-white.png';
	else if (id === 200)  img = '../sprites/ori-skul.png';
	let ico = new Leaflet.Icon({iconUrl: img, iconSize: new Leaflet.Point(48, 48)});
	return ico
};

function get_inner(id) {
	return (
	<Tooltip>
	<span>{id}</span>
	</Tooltip>
	);
};

const PlayerMarker = ({ map, position, icon, inner}) => (
	<Marker map={map} position={position} icon={icon}>
		{inner}
	</Marker>
	)

const PlayerMarkersList = ({map, players}) => {
	let players_to_show = [];
	Object.keys(players).map((id) => {
		if(players[id].flags.includes("show_marker"))
			players_to_show.push(id)
	});
	const items = players_to_show.map((id) => (
		<PlayerMarker  key={"player_"+id} map={map} position={players[id].pos} inner={get_inner(id)} icon={player_icons(id)}  />
	));
	return (<div style={{display: 'none'}}>{items}</div>);
}

const PlayerUiOpts = ({players, setter}) => {
	if(!players || Object.keys(players).length === 0)
		return null;
	const items = Object.keys(players).map((id) => {
		let f = (newFlags) => setter((prevState) => {
			let retVal = prevState.players;
			retVal[id].flags = newFlags;
			return {players:retVal};
		});
		return (
			<div class="player-wrapper">
				<span class="player-name">Player {id}</span>
				<CheckboxGroup class="player-options" checkboxDepth={4} name={id+"_flags"} value={players[id].flags} onChange={f}>
					<label><Checkbox value="show_marker"/> Show on map</label>
					<label><Checkbox value="show_spoiler"/> Show spoilers</label>
					<label><Checkbox value="hide_found"/> Hide found</label>
					<label><Checkbox value="hide_unreachable"/> Hide unreachable</label>
					<label><Checkbox value="hide_remaining"/> Hide remaining</label>
					<label><Checkbox value="hot_assist"/> Split assist mode</label>
		    </CheckboxGroup>
			</div>
		);
	});
	return (<div>{items}</div>);
}

function getLocInfo(pick, players) {
	let loc = pick.loc;
	let info = Object.keys(players).map((id) => {
		let show_spoiler = players[id].flags.includes("show_spoiler");
		let seen = players[id].seen.includes(loc);
		if(show_spoiler || seen)
			return id + ":" + players[id].seed[loc] + ((show_spoiler && seen) ? "*" : "");
		else
			return id + ":" + "(hidden)"
	});
	return info;
}

function getPickupMarkers(state) {
	let players = state.players;
	let hideOpt = state.hideOpt;
	let pickupTypes = state.pickups;
	let markers = []
	for(let i in pickupTypes) {
		let pre = pickupTypes[i];
		for(let p in picks_by_type[pre]) {
			let pick = picks_by_type[pre][p]
			let count = Object.keys(players).length
			let x = pick.hasOwnProperty("_x") ? pick._x : pick.x
			let y = pick.hasOwnProperty("_y") ? pick._y : pick.y
			let icon = pick.hasOwnProperty("icon") ? pick.icon : pickup_icons[pre]
			if(count === 0) {
				markers.push({key: pick.name+"|"+pick.x+","+pick.y, position: [y, x], inner: null, icon: icon})
				continue
			}
			let is_hot = false;
			let highlight = false;
			Object.keys(players).map((id) => {
				let player = players[id]
				let hide_found = player.flags.includes("hide_found")
				let hide_unreachable = player.flags.includes("hide_unreachable")
				let hide_remaining = player.flags.includes("hide_remaining")
				let hot_assist = player.flags.includes("hot_assist")
				let show_spoiler = player.flags.includes("show_spoiler");
				let pick_name = player.seed[pick.loc]
				let found = player.seen.includes(pick.loc);
				if(!is_hot && found &&  pick_name === "Warmth Returned")
					is_hot = true;
				if(is_hot && !found && hot_assist)
					highlight = true;
				if(!highlight && (found || show_spoiler) && state.searchStr && pick_name.toLowerCase().includes(state.searchStr.toLowerCase()))
					highlight = true;
				let reachable = players[id].areas.includes(pick.area);

				if( (found && hide_found) || (!found && hide_remaining) || (!reachable && hide_unreachable && !found))
					count -= 1;
			});

			if((hideOpt === "any") ? (count === Object.keys(players).length) : (count > 0))
			{
				let loc_info = getLocInfo(pick, players);
				let inner = null;
				if(loc_info)
					{
					let lines = loc_info.map((infoln) => {
						return (
						<tr><td style={{color:'black'}}>{infoln + (is_hot ? " !hot!" : "")}</td></tr>
						)
					});
					inner = (
					<Tooltip>
						<table>
						{lines}
						</table>
					</Tooltip>
					);
				}
				if(highlight)
					icon = new Leaflet.Icon({iconUrl: icon.options.iconUrl, iconSize: new Leaflet.Point(icon.options.iconSize.x*2, icon.options.iconSize.y*2)})
				markers.push({key: pick.name+"|"+pick.x+","+pick.y, position: [y, x], inner: inner, icon: icon});
			}

		}
	}
	return markers;
};

(function(){
    var originalInitTile = Leaflet.GridLayer.prototype._initTile
    Leaflet.GridLayer.include({
        _initTile: function (tile) {
            originalInitTile.call(this, tile);

            var tileSize = this.getTileSize();

            tile.style.width = tileSize.x + 1 + 'px';
            tile.style.height = tileSize.y + 1 + 'px';
        }
    });
})();

const DEFAULT_VIEWPORT = {
	  center: [0, 0],
	  zoom: 3,
	};
const RETRY_MAX = 60;
const TIMEOUT_START = 5;
const TIMEOUT_INC = 5;

const crs = getMapCrs();

class GameTracker extends React.Component {
  constructor(props) {
    super(props)
    let modeRaw = document.getElementsByClassName("logic-modes")[0].id
    let modes = (modeRaw !== "None") ? modeRaw.split(" ") : ['normal', 'speed', 'dboost-light', 'lure']

    this.state = {players: {}, retries: 0, check_seen: 1, modes: modes, timeout: TIMEOUT_START, searchStr: "",
    flags: ['show_pickups', 'update_in_bg'], viewport: DEFAULT_VIEWPORT, pickups: ["EX", "HC", "SK", "Pl", "KS", "MS", "EC", "AC", "EV"],
    pathMode: 'standard', hideOpt: "all", display_logic: false};
  };

  componentDidMount() {
	  this.interval = setInterval(() => this.tick(), 1000);
  };

  timeout = () => {
  	return {retries: this.state.retries+1, check_seen: this.state.timeout, timeout: this.state.timeout+TIMEOUT_INC}
  };
  tick = () => {
  	if(this.state.retries >= RETRY_MAX) return;
  	if(!document.hasFocus() && !this.state.flags.includes("update_in_bg")) return;

  	if(this.state.check_seen == 0) {
	  	this.setState({check_seen: 5});
		getSeen((p) => this.setState(p), this.timeout);
		getReachable((p) => this.setState(p),this.state.modes.join("+"), this.timeout);
		Object.keys(this.state.players).map((id) => {
			if(Object.keys(this.state.players[id].seed).length < 50)
				getSeed((p) => this.setState(p), id, this.timeout);
		})
  	} else
	  		this.setState({check_seen: this.state.check_seen -1});
		if(this.state.check_seen < 10)
			getPlayerPos((p) => this.setState(p), this.timeout);
  };

  componentWillUnmount() {
    clearInterval(this.interval);
  };

  hideOptChanged = newVal => { this.setState({hideOpt: newVal}) }
  flagsChanged = newVal => { this.setState({flags: newVal}) }
  pickupsChanged = newVal => { this.setState({pickups: newVal}) }
  modesChanged = newVal => { this.setState({modes: newVal}, () => getReachable((p) => this.setState(p),this.state.modes.join("+"))) }
  onSearch = event => { this.setState({searchStr: event.target.value}) }

	toggleLogic = () => {this.setState({display_logic: !this.state.display_logic})};

  onViewportChanged = viewport => { this.setState({ viewport }) }
 _onPathModeChange = (n) => paths.includes(n.value) ? this.setState({modes: presets[n.value], pathMode: n.value}, () => getReachable((p) => this.setState(p),this.state.modes.join("+"))) : this.setState({pathMode: n.value})

  render() {
		const pickup_markers = this.state.flags.includes('show_pickups') ? ( <PickupMarkersList markers={getPickupMarkers(this.state)} />) : null;
		const player_markers = ( <PlayerMarkersList players={this.state.players} />)
		const player_opts = ( <PlayerUiOpts players={this.state.players} setter={(p) => this.setState(p)} />)
    return (
			<div className="wrapper">
      	<Map crs={crs} onViewportChanged={this.onViewportChanged} viewport={this.state.viewport}>
					<TileLayer url=' https://ori-tracker.firebaseapp.com/images/ori-map/{z}/{x}/{y}.png' noWrap='true' />
					{pickup_markers}
					{player_markers}
		    </Map>
				<div className="controls">
		    	<div id="search-wrapper">
						<label for="search">Search</label>
						<input id="search" className="form-control" type="text" value={this.state.searchStr} onChange={this.onSearch} />
					</div>
					<Button onClick={() => this.setState({ viewport: DEFAULT_VIEWPORT })}>Reset View</Button>
					<div id="map-controls">
						<span className="control-label"><h5>Flags</h5></span>
						<CheckboxGroup style={{paddingLeft: '8px', paddingRight: '8px'}} checkboxDepth={3} name="flags" value={this.state.flags} onChange={this.flagsChanged}>
			        <label><Checkbox value="show_pickups"/> Pickups</label>
							<label><Checkbox value="update_in_bg"/> Always Update</label>
		       </CheckboxGroup>
					</div>
					<div id="player-controls">
						<span className="control-label"><h5>Players</h5></span>
						{player_opts}
						<div style={{paddingLeft: '8px', paddingRight: '8px'}}>
							<span>Hide pickup if it would be hidden for...</span>
							<RadioGroup name="hideOpts" selectedValue={this.state.hideOpt} onChange={this.hideOptChanged}>
								<label><Radio value="all"/> ...all players</label>
								<label><Radio value="any"/> ...any player</label>
		       		</RadioGroup>
						</div>
					</div>
					<div id="logic-controls">
						<div id="logic-presets">
			      	<Button color="primary" onClick={this.toggleLogic} >Logic Presets:</Button>
			      	<Select options={paths.map((n) => {return {label: n, value: n}})} onChange={this._onPathModeChange} clearable={false} value={this.state.pathMode} label={this.state.pathMode}></Select>
						</div>
						<Collapse id="logic-options-wrapper" isOpen={this.state.display_logic}>
							<CheckboxGroup id="logic-options" checkboxDepth={4} name="modes" value={this.state.modes} onChange={this.modesChanged}>
								<label><Checkbox value="normal" /> normal</label>
								<label><Checkbox value="speed" /> speed</label>
								<label><Checkbox value="extended" /> extended</label>
								<label><Checkbox value="speed-lure" /> speed-lure</label>
								<label><Checkbox value="lure" /> lure</label>
								<label><Checkbox value="lure-hard" /> lure-hard</label>
								<label><Checkbox value="dboost-light" /> dboost-light</label>
								<label><Checkbox value="dboost" /> dboost</label>
								<label><Checkbox value="dboost-hard" /> dboost-hard</label>
								<label><Checkbox value="cdash" /> cdash</label>
								<label><Checkbox value="cdash-farming" /> cdash-farming</label>
								<label><Checkbox value="extreme" /> extreme</label>
								<label><Checkbox value="extended-damage" /> extended-damage</label>
								<label><Checkbox value="timed-level" /> timed-level</label>
								<label><Checkbox value="dbash" /> dbash</label>
								<label><Checkbox value="glitched" /> glitched</label>
					  	</CheckboxGroup>
						</Collapse>
					</div>
					<div id="pickup-controls">
						<span className="control-label"><h5>Visible Pickups</h5></span>
						<CheckboxGroup id="pickup-wrapper" checkboxDepth={4} name="options" value={this.state.pickups} onChange={this.pickupsChanged}>
							<label><Checkbox value="SK" />Skill trees</label>
							<label><Checkbox value="MS" />Mapstones</label>
							<label><Checkbox value="EV" />Events</label>
							<label><Checkbox value="AC" />Abiliy Cells</label>
							<label><Checkbox value="HC" />Health Cells</label>
							<label><Checkbox value="EC" />Energy Cells</label>
							<label><Checkbox value="Pl" />Plants</label>
							<label><Checkbox value="KS" />Keystones</label>
							<label><Checkbox value="EX" />Exp Orbs</label>
		    		</CheckboxGroup>
					</div>
				</div>
			</div>
		)
	}
};

function doNetRequest(onRes, setter, url, timeout)
{
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.onreadystatechange = function() {
        if (xmlHttp.readyState === 4) {
        	 if(xmlHttp.status === 404)
        	 	setter(timeout())
        	 else
	        	 onRes(xmlHttp.responseText);
        }
	}
    xmlHttp.open("GET", url, true); // true for asynchronous
    xmlHttp.send(null);
}

function getSeed(setter, pid, timeout)
{
     var onRes = (res) => {
				setter((prevState, props) => {
					let retVal = prevState.players;
					retVal[pid].seed = parse_seed(res);
					return {players:retVal, retries: 0, timeout: TIMEOUT_START}
				});
            }
     doNetRequest(onRes, setter, "/"+game_id+"."+pid+"/_seed", timeout)
}



function getReachable(setter, modes, timeout) {
     var onRes = (res) => {
            	let areas = {};
            	let raw = res.split("|");
            	for (let i = 0, len = raw.length; i < len; i++) {
            		let withid = raw[i].split(":");
            		if(withid[1] == "")
            			continue;
            		let id = withid[0];
					areas[id] = withid[1].split(",");
				}
				setter((prevState, props) => {
					let retVal = prevState.players
					Object.keys(areas).map((id) => {
						if(!retVal.hasOwnProperty(id)){
							retVal[id] = {...EMPTY_PLAYER};
						}
						retVal[id].areas = areas[id]
					})
					return {players:retVal, retries: 0, timeout: TIMEOUT_START}
				})
    }
    doNetRequest(onRes, setter, "/"+game_id+"/_reachable?modes="+modes, timeout)
}

function getSeen(setter, timeout)
{
     var onRes = (res) => {
            	let seens = {};
            	let raw = res.split("|");
            	for (let i = 0, len = raw.length; i < len; i++) {
            		let withid = raw[i].split(":");
            		if(withid[1] == "")
            			continue;
            		let id = withid[0];
					seens[id] = withid[1].split(",").map((i) => parseInt(i));
				}
				setter((prevState, props) => {
					let retVal = prevState.players
					Object.keys(seens).map((id) => {
						if(!retVal.hasOwnProperty(id)){
							retVal[id] = {...EMPTY_PLAYER};
						}
						retVal[id].seen = seens[id]
					})
					return {players:retVal, retries: 0, timeout: TIMEOUT_START}
				})
    }
    doNetRequest(onRes, setter, "/"+game_id+"/_seen", timeout)
}


function getPlayerPos(setter, timeout)
{
     var onRes = (res) => {
            	let player_positions = {};
            	let rawpos = res.split("|");
            	for (let i = 0, len = rawpos.length; i < len; i++) {
            		let withid = rawpos[i].split(":");
            		let id = withid[0];
            		let pos = withid[1].split(",");
					player_positions[id] = [pos[1]*1.0, pos[0]*1.0];
				}
				setter((prevState, props) => {
					let retVal = prevState.players
					Object.keys(player_positions).map((id) => {
						if(!retVal.hasOwnProperty(id))
							retVal[id] = {...EMPTY_PLAYER};
						retVal[id].pos = player_positions[id]
					})
					return {players:retVal, retries: 0, timeout: TIMEOUT_START}
				})
    }
    doNetRequest(onRes, setter, "/"+game_id+"/_getPos", timeout)
}


export default GameTracker;
