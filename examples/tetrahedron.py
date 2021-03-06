import glfw
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import numpy as np
from os import read
import pyrr
from math import sqrt
vertex_src = """
# version 330
in vec3 a_position;
in vec3 a_color;//attribute color
out vec3 v_color;//varying color

uniform mat4 rotation;

void main()
{
    gl_Position = rotation*vec4(a_position, 1.0);
    v_color = a_color;
}
"""

fragment_src = """
# version 330
in vec3 v_color;
out vec4 out_color;
void main()
{
    out_color = vec4(v_color, 1.0);
}
"""

# initializing glfw library
if not glfw.init():
    raise Exception("glfw can not be initialized!")

# creating the window
window = glfw.create_window(1280, 720, "My OpenGL window", None, None)

# check if window was created
if not window:
    glfw.terminate()
    raise Exception("glfw window can not be created!")

# set window's position
glfw.set_window_pos(window, 400, 200)

# make the context current
glfw.make_context_current(window)

vertices = [sqrt(8/9), -1/3, 0.0, 1.0, 0.0, 0.0,
             -sqrt(2/9), -1/3, -sqrt(2/3), 0.0, 1.0, 0.0,
             -sqrt(2/9),  -1/3, sqrt(2/3), 0.0, 0.0, 1.0,
             0.0, 1.0, 0.0, 1.0, 0.5, 0.0]

vertices = np.array(vertices, dtype=np.float32)

indices = [0,1,2,
        3,0,2,
        0,3,1,
        1,2,3]
indices = np.array(indices,dtype=np.uint32)

# vertexShader = glCreateShader(GL_VERTEX_SHADER)
# vertexShader = glShaderSource(vertexShader,1,vertex_src)
# compileShader(vertex_src)
shader = compileProgram(compileShader(vertex_src, GL_VERTEX_SHADER), compileShader(fragment_src, GL_FRAGMENT_SHADER))

#don't need this in python for some reason?
# VAO = glGenVertexArrays(1)
# glBindVertexArray(VAO)

VBO = glGenBuffers(1)#VBO stands for "vertex buffer object", and this is just the integer ID of that object
glBindBuffer(GL_ARRAY_BUFFER, VBO)#binds the GL_ARRAY_BUFFER to the buffer we just made, so now referencing GL_ARRAY_BUFFER means referencing the vbo object we made
glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)#puts the vertex data into the buffer we created

EBO = glGenBuffers(1)
glBindBuffer(GL_ELEMENT_ARRAY_BUFFER,EBO)
glBufferData(GL_ELEMENT_ARRAY_BUFFER,indices.nbytes,indices,GL_STATIC_DRAW)

position = glGetAttribLocation(shader, "a_position")#gets the integer position of the a_position variable from the shader, which we could've set with "layout (location=0) in vec3 a_position"
glEnableVertexAttribArray(position)
glVertexAttribPointer(position, 3, GL_FLOAT, GL_FALSE, vertices.itemsize*6, ctypes.c_void_p(0))#starts at 0 and stride is 24 bytes, so it skips over the color info that follows each vertex

color = glGetAttribLocation(shader, "a_color")#integer location of a_color variable in the shader.
glEnableVertexAttribArray(color)
glVertexAttribPointer(color, 3, GL_FLOAT, GL_FALSE, vertices.itemsize*6, ctypes.c_void_p(12))#starts at 12 abd strude us 24, so it starts at the color and skips the vertex info

glUseProgram(shader)
glClearColor(0, 0.1, 0.1, 1)#sets clear color
glEnable(GL_DEPTH_TEST)
def framebuffer_size_callback(window,width,height):
    glViewport(0,0,width,height)

def process_input(window):
    if glfw.get_key(window,glfw.KEY_ESCAPE) == glfw.PRESS:
        glfw.set_window_should_close(window,True)

glfw.set_framebuffer_size_callback(window,framebuffer_size_callback)
rot_location = glGetUniformLocation(shader,"rotation")
# the main application loop
while not glfw.window_should_close(window):
    process_input(window)
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

    rot_matrix = pyrr.Matrix44.from_y_rotation(glfw.get_time())#np.array([0,1,0,0.5*glfw.get_time()],dtype=np.float32)
    #print(rot_matrix)
    glUniformMatrix4fv(rot_location,1,GL_FALSE,rot_matrix)
    #glBindBuffer(GL_ELEMENT_ARRAY_BUFFER,EBO)
    #glDrawArrays(GL_TRIANGLES, 0,6)
    glDrawElements(GL_TRIANGLES,len(indices),GL_UNSIGNED_INT,ctypes.c_void_p(0))#this was the big error causing white screen of death in the program. The last argument should be None, not 0. The problem was that I just translated the parameters straight from the book, where the code is in C++

    glfw.poll_events()
    glfw.swap_buffers(window)

# terminate glfw, free up allocated resources
glfw.terminate()