const LINE_SPACING = 30;
const GAP = 10;

class Nodo {
    constructor(id) {
        this.id = id;
        this.linea = new Line();
        this.bounding_box = new Box();
        this.children = [];
        this.final = false;
        this.reference = false;
        this.elem = document.createElement("div")
        this.elem.innerHTML = `<span>${id}</span>`;
        this.elem.classList.add("card");
        document.getElementById("graph_view").appendChild(this.elem)
        this.rect = new Box(0,0,50,30);
        this.rect = box_from_elem(this.elem);
    }

    compute_box() {
        this.bounding_box = this.rect.copy();
        if (this.children.length==0) return;
        for (let child of this.children) {
            child.compute_box();
        }
        
        let child_width = this.children.reduce((acc,n)=>acc+n.bounding_box.w, 0) + Math.max(0,GAP*(this.children.length-1));

        this.bounding_box.w = Math.max(child_width, this.rect.w);
        this.bounding_box.h = this.rect.h + LINE_SPACING + this.children.reduce((a,b)=>Math.max(a,b.bounding_box.h),0);
        
        this.rect.x = (this.bounding_box.w-this.rect.w)/2
        
        let point = 0;
        const children_y = this.rect.h + LINE_SPACING;
        for (let child of this.children) {
            child.moveto(point,children_y);
            point += child.bounding_box.w + GAP;
        }
    }

    compute_lines() {
        if (this.children.length==0) return;
        if (this.children.length==1) {
            this.linea.segments.push(new Segment(
                this.rect.x + this.rect.w/2,
                this.rect.y + this.rect.h,
                this.rect.x + this.rect.w/2,
                this.rect.y + this.rect.h + LINE_SPACING,
            ));
            this.linea.bounding_box.x = this.linea.a-5;
            this.linea.bounding_box.y = this.linea.b;
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
    const visited = [];
    const head = new Nodo(0);

    const queue = [head];
    while (queue.length>0) {
        const corrente = queue.pop();
        const raw = raw_nodes[corrente.id];
        visited.push(corrente.id)

        if (raw.is_final) {
            corrente.final=true;
            corrente.elem.classList.add("finale");
        }
        
        if (raw.children) {
            for (let child_id of raw.children) {
                const new_son = new Nodo(child_id);
                if (visited.includes(child_id)) {
                    new_son.reference = true;
                    new_son.elem.classList.add("dummy")
                }else{
                    queue.unshift(new_son);
                }
                corrente.children.push(new_son);
            }
        }
    }

    head.compute_box();
    head.compute_lines();
    return head;
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
    constructor() {
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
