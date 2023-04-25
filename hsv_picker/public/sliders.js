function start() {
    class HSV {
        constructor(h, s, v) {
            this.h = h;
            this.s = s;
            this.v = v;
        }
        static rgbToHsv (r, g, b) {
            let rabs, gabs, babs, rr, gg, bb, h, s, v, diff, diffc, percentRoundFn;
            rabs = r / 255;
            gabs = g / 255;
            babs = b / 255;
            v = Math.max(rabs, gabs, babs),
            diff = v - Math.min(rabs, gabs, babs);
            diffc = c => (v - c) / 6 / diff + 1 / 2;
            percentRoundFn = num => Math.round(num * 100) / 100;
            if (diff == 0) {
                h = s = 0;
            } else {
                s = diff / v;
                rr = diffc(rabs);
                gg = diffc(gabs);
                bb = diffc(babs);
        
                if (rabs === v) {
                    h = bb - gg;
                } else if (gabs === v) {
                    h = (1 / 3) + rr - bb;
                } else if (babs === v) {
                    h = (2 / 3) + gg - rr;
                }
                if (h < 0) {
                    h += 1;
                }else if (h > 1) {
                    h -= 1;
                }
            }
            return new HSV(Math.round(h * 360),
                percentRoundFn(s * 100),
                percentRoundFn(v * 100));
        }
        static inRange(min, max, v) {
            return (min.h <= v.h) && (min.s <= v.s) && (min.v <= v.v) && (max.h >= v.h) && (max.s >= v.s) && (max.v >= v.v);
        }
    }

    function update(ctx, maskCtx, label, slider) {
        ctx.drawImage(img, 0, 0);
        imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
        maskCtx.drawImage(img, 0, 0);

        let hsvData = [];
        for (let i = 0; i < imageData.data.length; i += 4) {
            let hsv = HSV.rgbToHsv(imageData.data[i], imageData.data[i + 1], imageData.data[i + 2]);
            hsvData.push(hsv);
        }

        const copy = new ImageData(
            new Uint8ClampedArray(imageData.data),
            imageData.width,
            imageData.height
          );
        if (label) {
            label.innerHTML = `${label.id}: ${slider.value}`
            const [prop, index] = slider.id.split('');
            maskBounds[index][prop] = Number(slider.value);
        }
        
        
        for (let i = 0; i < hsvData.length; i++) {
            if (!HSV.inRange(maskBounds[0], maskBounds[1], hsvData[i])) {
                // Blacks out the pixel if out of range
                copy.data[4 * i] = 0;
                copy.data[4 * i + 1] = 0;
                copy.data[4 * i + 2] = 0;
            }
        }
        maskCtx.putImageData(copy, 0, 0)
    }
    
    
    const DEFAULT_PATH = './birds.jpg';
    const img = new Image();
    let canvas = document.getElementById("hsv");
    let dest = document.getElementById("mask");
    let maskBounds = [new HSV(0, 0, 0), new HSV(360, 100, 100)]
    
    /*let websocket = new WebSocket('ws://localhost:8000/');
    websocket.binaryType = 'blob';*/

    img.crossOrigin = "anonymous";
    img.src = DEFAULT_PATH;
    img.style = 'display: none;';
    document.getElementById('body').appendChild(img);

    let imageData;
    let ctx = canvas.getContext('2d', {"willReadFrequently": true});
    let maskCtx = dest.getContext('2d', {"willReadFrequently": true});

    img.onload = function () {
        console.log("Loaded!");
        canvas.width = this.width;
        canvas.height = this.height;
        dest.width = this.width;
        dest.height = this.height;

        const sliderContainers = document.querySelectorAll(".slider-container");
        for (let container of sliderContainers) {
            let [slider, label] = container.children;
            label.innerHTML = `${label.id}: ${slider.value}`;
            const newUpdate = () => {update(ctx, maskCtx, label, slider)};
            newUpdate();
            slider.oninput = newUpdate;
        };

        /*websocket.addEventListener('message', ({data}) => {
            let blobURL = URL.createObjectURL(data);
            img.src = blobURL;
            update(ctx, maskCtx, null, null);
        });*/
    }
}

document.addEventListener('DOMContentLoaded', start, false);