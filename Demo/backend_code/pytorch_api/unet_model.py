import numpy as np
import torch
import os
from collections import OrderedDict
from torch.autograd import Variable
from base_model import BaseModel
import networks
from PIL import ImageOps,Image
import time

def tensor2im(image_tensor, imtype=np.uint8):
    image_numpy = image_tensor[0].cpu().float().numpy()
    image_numpy = np.transpose(image_numpy,(1,2,0))
    image_numpy = (image_numpy + 1) / 2.0 * 255.0
    if image_numpy.shape[2] == 8:
        a = np.tile(np.expand_dims(np.mean(image_numpy,axis=2),axis=2),(1,1,3))
        image_numpy = Image.fromarray(a.astype(np.uint8))
        #image_numpy = Image.fromarray(np.uint8(image_numpy[:,:,0:3]))
    elif image_numpy.shape[2] == 1:
        image_numpy = np.tile(image_numpy, (1,1,3))
    image_numpy  = np.asarray(image_numpy)
    return image_numpy.astype(imtype)

def png2patches(png,step,size):
    step = np.int32(step)
    size=  np.int32(size)
    w,h,z = png.shape
    ni = np.int32(np.floor((w- size)/step) +2)

    nj = np.int32(np.floor((h- size)/step) +2)

    patches = np.zeros((ni,nj,size,size,z))
    for i in range(0,ni-1):
        for j in range(0,nj-1):
            patches[i,j,:,:,:] = png[i*step:i*step+size,j*step:j*step+size,:]
    for i in range(0,ni-1):
        patches[i,nj-1,:,:,:] = png[i*step:i*step+size,h-size:h,:]

    for j in range(0,nj-1):
        patches[ni-1,j,:,:,:] = png[w-size:w,j*step:j*step+size,:]
    patches[ni-1,nj-1,:,:,:] = png[w-size:w,h-size:h,:]
    return patches

def patches2png_legacy(patches,w,h,step,size):
    tif = np.zeros((1,w,h))
    ws = np.zeros((1,w,h))
    
    ni = np.int32(np.floor((w- size)/step) +2)

    nj = np.int32(np.floor((h- size)/step) +2)
    for i in range(0,ni-1):
        for j in range(0,nj-1):
            tif[:,i*step:i*step+size,j*step:j*step+size]=  tif[:,i*step:i*step+size,j*step:j*step+size]+ patches[i,j,:,:,:]
            ws[:,i*step:i*step+size,j*step:j*step+size]=  ws[:,i*step:i*step+size,j*step:j*step+size]+ 1
           
    for i in range(0,ni-1):
        tif[:,i*step:i*step+size,h-size:h] =  tif[:,i*step:i*step+size,h-size:h]+ patches[i,nj-1,:,:,:] 
        ws[:,i*step:i*step+size,h-size:h] =  ws[:,i*step:i*step+size,h-size:h]+ 1

    for j in range(0,nj-1):
        tif[:,w-size:w,j*step:j*step+size]= tif[:,w-size:w,j*step:j*step+size]+ patches[ni-1,j,:,:,:]
        ws[:,w-size:w,j*step:j*step+size]= ws[:,w-size:w,j*step:j*step+size]+ 1
   
    tif[:,w-size:w,h-size:h] = tif[:,w-size:w,h-size:h]+ patches[ni-1,nj-1]
    ws[:,w-size:w,h-size:h] = ws[:,w-size:w,h-size:h]+ 1
    
    tif = np.divide(tif,ws)
    return tif

class UnetModel(BaseModel):
    def name(self):
        return 'UnetCodeforAPI'
    def eval(self):
        self.netG.eval()
    def initialize(self, model_path):
        # load/define networks
        self.netG = networks.define_G(3, 1, 64,
                                      'unet_256', norm = 'instance')
        self.netG.load_state_dict(torch.load(model_path)) 


    def get_prediction(self,image_bytes):

        if not image_bytes:
            raise ValueError('Input image is empty')
        try:
            img = Image.open(image_bytes)
        except:
            raise ValueError('Cannot read the Input image')

        if image.mode not in ('RGBA','RGB'):
            raise AttributeError('Input image not in RGBA or RGB mode and cannot be processed.')
        if image.mode =='RGBA':
            image = image.convert(mode='RGB')
        if img.size[0]<256 or img.size[1]<256:
            raise ValueError('Input image size is too small, the minimum size is 256x256')

        if img.size[0]>2048 or img.size[1]<2048:
            raise ValueError('Input image size is too big, the maximum size is 2048x2048')
        img = img.resize((1024,1024))
        image_np = np.asarray(img, np.float)
        image_np = ((image_np/255)-0.5)*2
        print(image_np.shape)

        # swap color axis because numpy image is H x W x C, torch image is C X H X W
        image_np = image_np.transpose((2, 0, 1))
        image_np = image_np[:3, :, :] # Remove the alpha channel
        image_np = np.expand_dims(image_np, axis=0)  # add a batch dimension
        img_input = torch.from_numpy(image_np).type(torch.float32)

        self.input = Variable(img_input)
        self.output = self.netG(self.input)
        raw = self.output.data.cpu().float().numpy()
        raw = np.transpose(raw,(0,2,3,1))
        raw = raw[0,:,:,0]
        raw = (raw +1) /2 
        raw = (raw*255).astype(np.uint8)
        print(raw.shape)
        return raw
    
    def png_predict(self,image_bytes):
        img = Image.open(image_bytes)
        im = np.asarray(img)
#        im = image_bytes
        last = time.time()
        step = 128
        size = 256
        w,h,c = im.shape
        patches = png2patches(im,step,size)
        print(patches.shape)
        elapsed_time = time.time() - last
        last = time.time()
        print('im 2 patches: %0.4f'%(elapsed_time))

        orishape = np.asarray(patches.shape)
        orishape[-1] = 1

        patches = np.reshape(patches, (-1,256,256,3))
        outshape  = np.asarray(patches.shape)
        outshape[3] = 1
        patches = np.transpose(patches,(0,3,1,2))
        s = np.asarray(patches.shape)
        s[1] = 1
        bs = 32
        n_patches = patches.shape[0]
        out = np.zeros(s) 
        print('numbers of patches %d'%(n_patches))
        print('Processing all patches')
        for i in range(0,n_patches,bs):
            batch  = patches[i:i+bs,:,:,:]
            batch = torch.from_numpy(batch).float().div(255)
            batch = (batch  - 0.5) * 2
            temp = self.netG(batch)
            out[i:i+bs,:,:,:] = temp.detach().numpy()

        elapsed_time = time.time() - last
        last = time.time()
        print('patches 2 prediction: %0.4f'%(elapsed_time))
        out = np.reshape(out,outshape)
        out = np.reshape(out,(orishape[0],orishape[1],outshape[3],outshape[1],outshape[2]))
        print(out.shape)

        outpng = patches2png_legacy(out,w,h,step,size)
        print(outpng.shape)
        print('merging')
        outpng = np.transpose(outpng,(1,2,0))
        outpng = np.squeeze(outpng) 
        outpng = (outpng + 1)/2
        out = outpng
        outpng = outpng*255
        return outpng



if __name__=='__main__':
    M = UnetModel()
    M.initialize('300_net_G.pth')
    print(M.netG)
    a = np.random.rand(2000,2000,3)
    print(a.shape)
    b = M.png_predict(a)
    print(b.shape)
    b = Image.fromarray(b).convert('L')
    b.save("out.png")
