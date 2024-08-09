import { start_choice } from "./choice_modal.js";

const LINE_SPACING = 50;
const GAP = 10;

class Nodo {
    constructor(id, raw) {
        this.id = id;
        this.linea = new Line(id);
        this.bounding_box = new Box();
        this.children = [];
        this.final = false;
        this.reference = false;
        this.choice = raw.choice;

        this.elem = create_card(id, raw); 
        this.rect = box_from_elem(this.elem);

        if (raw.choice)
            this.legend = create_legend(raw.choice);

        this.is_loop = false;
    }

    compute_box() {
        this.bounding_box = this.rect.copy();
        if (this.children.length==0) return;
        for (let child of this.children) {
            child.compute_box();
        }
        
        let child_width = this.children.reduce((acc,n)=>acc+n.bounding_box.w, 0) + Math.max(0,GAP*(this.children.length-1));
        
        let legend_width = 0;
        if (this.legend)
            legend_width = this.legend.getBoundingClientRect().width;

        this.bounding_box.w = Math.max(child_width, this.rect.w);
        this.bounding_box.h = this.rect.h + LINE_SPACING + this.children.reduce((a,b)=>Math.max(a,b.bounding_box.h),0);
        
        this.rect.x = (this.bounding_box.w-this.rect.w)/2
        
        let point = (this.bounding_box.w - child_width )/2;
        const children_y = this.rect.h + LINE_SPACING;
        for (let child of this.children) {
            child.moveto(point,children_y);
            point += child.bounding_box.w + GAP;
        }

        this.bounding_box.w = Math.max(this.bounding_box.w, this.rect.x+this.rect.w/2+5+legend_width);
    }

    compute_lines() {
        if (this.children.length==0) return;
        if (this.children.length==1) {
            const segmento = new Segment(
                                this.rect.x + this.rect.w/2,
                                this.rect.y + this.rect.h,
                                this.rect.x + this.rect.w/2,
                                this.rect.y + this.rect.h + LINE_SPACING,
                            )
            this.linea.segments.push(segmento);
            this.linea.bounding_box.x = segmento.a-5;
            this.linea.bounding_box.y = segmento.b;
            this.linea.bounding_box.w = 10;
            this.linea.bounding_box.h = LINE_SPACING;
        }else{
            const horizontal_segment = new Segment(
                this.children[0].rect.x + this.children[0].rect.w/2,
                this.rect.y + this.rect.h + LINE_SPACING/2,
                this.children[this.children.length-1].rect.x + this.children[this.children.length-1].rect.w/2,
                this.rect.y + this.rect.h + LINE_SPACING/2,
            );
            this.linea.bounding_box.x = horizontal_segment.a;
            this.linea.bounding_box.y = this.rect.y + this.rect.h;
            this.linea.bounding_box.w = horizontal_segment.x - horizontal_segment.a;
            this.linea.bounding_box.h = LINE_SPACING;

            this.linea.segments.push(horizontal_segment);
            this.linea.segments.push(new Segment(
                this.rect.x + this.rect.w/2,
                this.rect.y + this.rect.h,
                this.rect.x + this.rect.w/2,
                this.rect.y + this.rect.h + LINE_SPACING/2,
            ));
            for (let child of this.children) {
                this.linea.segments.push(new Segment(
                    child.rect.x + child.rect.w/2,
                    child.rect.y - LINE_SPACING/2,
                    child.rect.x + child.rect.w/2,
                    child.rect.y,
                ));
            }
        }
        for (let child of this.children) {
            child.compute_lines()
        }
    }

    moveto(dest_x, dest_y) {
        const delta_x = dest_x - this.bounding_box.x;
        const delta_y = dest_y - this.bounding_box.y;
        this.moveby(delta_x, delta_y);
    }

    moveby(delta_x, delta_y) {
        this.bounding_box.x += delta_x;
        this.bounding_box.y += delta_y;
        this.rect.x += delta_x;
        this.rect.y += delta_y;

        this.linea.bounding_box.x += delta_x;
        this.linea.bounding_box.y += delta_y;
        for (let seg of this.linea.segments) {
            seg.a += delta_x
            seg.b += delta_y
            seg.x += delta_x
            seg.y += delta_y
        }

        for (let child of this.children) {
            child.moveby(delta_x,delta_y);
        }
    }
}

export function build_tree(raw_nodes) {
    const raw_nodes_map = {};
    for (let node of raw_nodes) {
        raw_nodes_map[node.id] = node;
    }

    const visited = [];
    const head = new Nodo(0, raw_nodes_map[0]);

    const queue = [head];
    while (queue.length>0) {
        const corrente = queue.pop();
        const raw = raw_nodes_map[corrente.id];
        visited.push(corrente.id)

        if (raw.is_final) {
            corrente.final=true;
            corrente.elem.classList.add("finale");
        }
        
        if (raw.children) {
            for (let child_id of raw.children) {
                const new_son = new Nodo(child_id, raw_nodes_map[child_id]);
                if (visited.includes(child_id)) {
                    new_son.reference = true;
                    new_son.elem.classList.add("dummy")
                    new_son.elem.innerHTML = `
                        <span>goto ${child_id}</span>
                    `;
                    new_son.rect = box_from_elem(new_son.elem);
                    new_son.legend?.remove()
                    new_son.legend = undefined;
                }else{
                    queue.unshift(new_son);
                }
                corrente.children.push(new_son);
            }
        }
    }

    find_loops(head, raw_nodes);

    head.compute_box();
    head.compute_lines();
    return head;
}

function find_loops(root, raw_nodes) {
    const nodi = get_nodes(root).filter(n=>!n.reference);
    const raw_map = {};
    const raw_map_reverted = {};
    for (let node of raw_nodes) {
        raw_map[node.id] = node;

        if (!(node.id in raw_map_reverted)) 
            raw_map_reverted[node.id] = {"id":node.id, "children":[]};
        if (!node.children) continue;

        for (let child_id of node.children) {
            if (!(child_id in raw_map_reverted)) 
                raw_map_reverted[child_id] = {"id":child_id, "children":[]};
            raw_map_reverted[child_id].children.push(node.id)
        }
    }

    const looping_nodes_ids = [];

    for (let raw_node of raw_nodes) {
        if (check_loop(raw_map, raw_map_reverted, raw_node.id)) {
            looping_nodes_ids.push(raw_node.id);
        }
    }

    for (let nodo of nodi) {
        if (looping_nodes_ids.includes(nodo.id)){
            nodo.is_loop = true;
            document.getElementById(`warning_${nodo.id}`).classList.remove("hidden");
        }
    }
}

function check_loop(raw_map, raw_map_reverse, id) {
    if (!raw_map[id].choice) return false;
    const reachable_forward = new Set();
    const reachable_backward = new Set();
    const stack = [id];
    while (stack.length > 0) {
        const id_corrente = stack.pop();
        if (reachable_forward.has(id_corrente)) continue;

        reachable_forward.add(id_corrente);
        const corrente = raw_map[id_corrente];
        if (!corrente.children) continue;
        for (let neighbor_id of corrente.children) {
            stack.push(neighbor_id);
        }
    }

    stack.push(id);
    while (stack.length > 0) {
        const id_corrente = stack.pop();
        if (reachable_backward.has(id_corrente)) continue;

        reachable_backward.add(id_corrente);
        const corrente = raw_map_reverse[id_corrente];
        for (let neighbor_id of corrente.children) {
            stack.push(neighbor_id);
        }
    }

    return ([...reachable_forward].every(x=>reachable_backward.has(x)))
}

export function get_nodes(root) {
    const ret = [];
    const queue = [root];
    while (queue.length>0) {
        const corrente = queue.pop();
        ret.push(corrente);
        queue.unshift(...corrente.children);
    }
    return ret;
}

class Line {
    constructor(id) {
        this.id=id;
        this.segments = [];
        this.bounding_box = new Box();
    }
}
class Segment {
    constructor(a,b,x,y) {
        this.a=a;
        this.b=b;
        this.x=x;
        this.y=y;
    }
}

class Box {
    constructor(x, y, w, h) {
        this.x = x;
        this.y = y;
        this.w = w;
        this.h = h;
    }

    copy() {
        return new Box(
            this.x,
            this.y,
            this.w,
            this.h
        );
    }

    contains(x,y) {
        return (x>this.x) && (x<this.x+this.w) && (y>this.y) && (y<this.y+this.h);
    }
}

function box_from_elem(elem) {
    const r = elem.getBoundingClientRect();
    return new Box(
        0,0,r.width,r.height
    );
}

let description_open = false;
let description_number=-1;
function create_card(id, raw) {
    const elem = document.createElement("div")
    const info_button_id = `info_button_${id}`;
    const choice_button_id = `choice_button_${id}`;
        elem.innerHTML = `
        <div>
            <span>${id}</span>
            <div>
                <button id="warning_${id}" class="warning hidden">loop!</button>
                <button id="${choice_button_id}" class="choice_button">choice</button>
                <button id="${info_button_id}" class="info_button">i</button>
            </div>
        </div>
        <hr/>
        `;
    if (id==0) {
        elem.innerHTML += "<span>Initial State</span>";
    }else{
        elem.innerHTML += raw.diff.map(x=>"<span>"+x+"</span>").join("<br/>");
    }
    elem.classList.add("card");
    document.getElementById("graph_view").appendChild(elem)
    document.getElementById(info_button_id).onclick = ()=>{
        click_card(id)
    };

    if (raw.choice) {
        document.getElementById(choice_button_id).remove();
    }else{
        document.getElementById(choice_button_id).onclick = ()=>{
            start_choice(id)
        };
    }
    return elem;
}

function create_legend(text) {
    const elem = document.createElement("span");
    elem.innerText = text;
    elem.classList.add("legend");
    document.getElementById("graph_view").appendChild(elem)
    return elem;
}

function click_card(id) {
    const state_description = document.getElementById("state_description");
    const horizontal_drag = document.getElementById("horizontal_drag");
    if (description_open && description_number==id) {
        state_description.style.display = "none";
        horizontal_drag.style.display = "none";
        description_open = false;
    }else{
        state_description.style.display = "unset";
        horizontal_drag.style.display = "unset";
        load_description(id);
        description_number = id;
        description_open = true;
    }
}

function load_description(id) {
    fetch(`state_description?id=${id}`)
        .then(res=>res.json())
        .then(data=>{
            let fluents = data.fluents;
            const state_name = document.getElementById("state_name");
            state_name.innerText = `State ${id}`;
            const state_params = document.getElementById("state_params");
            let lines = [];
            for (let name in fluents) {
                for (let a of fluents[name]) {
                    if (a.value!="false")
                        lines.push(`${name}[${a.parameters}] := ${a.value}`);
                }
            }
            state_params.innerHTML = lines.join("<br/>")
        });
}


