"""
Modern 3D Zia Fractal Renderer

A modern OpenGL (3.3+) implementation of the Zia fractal visualization.
Uses GLFW for window management and shaders for rendering.
"""

import glfw
import numpy as np
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import pyrr
from zia import Zia
import time

class Camera:
    def __init__(self):
        self.pos = pyrr.Vector3([0.0, 0.0, 15.0])
        self.front = pyrr.Vector3([0.0, 0.0, -1.0])
        self.up = pyrr.Vector3([0.0, 1.0, 0.0])
        self.right = pyrr.Vector3([1.0, 0.0, 0.0])
        self.yaw = -90.0
        self.pitch = 0.0
        self.speed = 5.0
        self.sensitivity = 0.1
        self.zoom = 45.0
        
    def get_view_matrix(self):
        return pyrr.matrix44.create_look_at(
            self.pos, 
            self.pos + self.front, 
            self.up
        )

class Zia3DModern:
    def __init__(self, width=1280, height=720, title="Zia 3D Modern"):
        self.width = width
        self.height = height
        self.title = title
        self.zia = Zia(1, 2, 1, npts=2000)
        self.camera = Camera()
        self.last_x, self.last_y = width / 2, height / 2
        self.first_mouse = True
        self.delta_time = 0.0
        self.last_frame = 0.0
        self.rotation = 0.0
        
        # Initialize GLFW
        if not glfw.init():
            raise Exception("GLFW can't be initialized")
            
        # Configure GLFW
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL_TRUE)
        
        # Create window
        self.window = glfw.create_window(width, height, title, None, None)
        if not self.window:
            glfw.terminate()
            raise Exception("GLFW window can't be created")
            
        # Make the window's context current
        glfw.make_context_current(self.window)
        
        # Set callbacks
        glfw.set_framebuffer_size_callback(self.window, self.framebuffer_size_callback)
        glfw.set_cursor_pos_callback(self.window, self.mouse_callback)
        glfw.set_scroll_callback(self.window, self.scroll_callback)
        
        # Capture the mouse
        glfw.set_input_mode(self.window, glfw.CURSOR, glfw.CURSOR_DISABLED)
        
        # Configure global OpenGL state
        glEnable(GL_DEPTH_TEST)
        
        # Generate Zia points first
        xpts, ypts = self.zia.genZia()
        zpts = np.zeros_like(xpts)
        
        # Create vertex data for cubes
        self.cube_size = 0.05
        self.vertices = []
        
        for x, y, z in zip(xpts, ypts, zpts):
            self.add_cube(x, y, z, self.cube_size)
            
        self.vertices = np.array(self.vertices, dtype=np.float32)
        
        # Setup VAO, VBO
        self.vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(1)
        
        # Bind the VAO first
        glBindVertexArray(self.vao)
        
        # Then bind and set vertex buffer(s) and attribute pointer(s)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)
        
        # Position attribute
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 6 * 4, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)
        
        # Color attribute
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 6 * 4, ctypes.c_void_p(3 * 4))
        glEnableVertexAttribArray(1)
        
        # Unbind VAO (it's always good to unbind any buffer/array to prevent strange bugs)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)
        
        # Now that VAO is set up, compile and link shaders
        self.shader_program = self.load_shaders()
        
        # Check if shader program was created successfully
        if not self.shader_program:
            print("Failed to create shader program. Check the logs above for errors.")
            return
            
        # Get uniform locations
        self.model_loc = glGetUniformLocation(self.shader_program, "model")
        self.view_loc = glGetUniformLocation(self.shader_program, "view")
        self.proj_loc = glGetUniformLocation(self.shader_program, "projection")
        
        # Check if uniforms were found
        if self.model_loc == -1 or self.view_loc == -1 or self.proj_loc == -1:
            print("Warning: One or more uniform locations not found in shader program")
    
    def add_cube(self, x, y, z, size):
        """Add a cube to the vertex list"""
        # Define the 8 vertices of the cube
        vertices = [
            # Front face
            x-size, y-size, z+size,  1.0, 0.0, 0.0,  # 0
            x+size, y-size, z+size,  1.0, 0.0, 0.0,  # 1
            x+size, y+size, z+size,  1.0, 0.0, 0.0,  # 2
            x-size, y+size, z+size,  1.0, 0.0, 0.0,  # 3
            # Back face
            x-size, y-size, z-size,  0.0, 1.0, 0.0,  # 4
            x+size, y-size, z-size,  0.0, 1.0, 0.0,  # 5
            x+size, y+size, z-size,  0.0, 1.0, 0.0,  # 6
            x-size, y+size, z-size,  0.0, 1.0, 0.0,  # 7
        ]
        
        # Define the 12 triangles that make up the cube (2 per face)
        indices = [
            0, 1, 2, 2, 3, 0,  # Front
            1, 5, 6, 6, 2, 1,   # Right
            7, 6, 5, 5, 4, 7,   # Back
            4, 0, 3, 3, 7, 4,   # Left
            4, 5, 1, 1, 0, 4,   # Bottom
            3, 2, 6, 6, 7, 3,   # Top
        ]
        
        # Add the vertices in the order specified by indices
        for i in indices:
            self.vertices.extend(vertices[i*6:i*6+6])
    
    def load_shaders(self):
        # Vertex shader
        vertex_shader_source = """#version 330 core
        layout (location = 0) in vec3 aPos;
        layout (location = 1) in vec3 aColor;
        
        out vec3 ourColor;
        
        uniform mat4 model;
        uniform mat4 view;
        uniform mat4 projection;
        
        void main()
        {
            gl_Position = projection * view * model * vec4(aPos, 1.0);
            ourColor = aColor;
        }
        """
        
        # Fragment shader
        fragment_shader_source = """#version 330 core
        out vec4 FragColor;
        
        in vec3 ourColor;
        
        void main()
        {
            FragColor = vec4(ourColor, 1.0);
        }
        """
        
        # Compile vertex shader
        vertex_shader = glCreateShader(GL_VERTEX_SHADER)
        glShaderSource(vertex_shader, vertex_shader_source)
        glCompileShader(vertex_shader)
        
        # Check vertex shader compilation
        if not glGetShaderiv(vertex_shader, GL_COMPILE_STATUS):
            error = glGetShaderInfoLog(vertex_shader).decode()
            print(f"Vertex shader compilation error:\n{error}")
            return None
        
        # Compile fragment shader
        fragment_shader = glCreateShader(GL_FRAGMENT_SHADER)
        glShaderSource(fragment_shader, fragment_shader_source)
        glCompileShader(fragment_shader)
        
        # Check fragment shader compilation
        if not glGetShaderiv(fragment_shader, GL_COMPILE_STATUS):
            error = glGetShaderInfoLog(fragment_shader).decode()
            print(f"Fragment shader compilation error:\n{error}")
            return None
        
        # Link shader program
        shader_program = glCreateProgram()
        glAttachShader(shader_program, vertex_shader)
        glAttachShader(shader_program, fragment_shader)
        glLinkProgram(shader_program)
        
        # Check linking errors
        if not glGetProgramiv(shader_program, GL_LINK_STATUS):
            error = glGetProgramInfoLog(shader_program).decode()
            print(f"Shader program linking error:\n{error}")
            return None
        
        # Clean up shaders (they're linked to the program now)
        glDeleteShader(vertex_shader)
        glDeleteShader(fragment_shader)
        
        return shader_program
    
    def process_input(self):
        if glfw.get_key(self.window, glfw.KEY_ESCAPE) == glfw.PRESS:
            glfw.set_window_should_close(self.window, True)
            
        camera_speed = self.camera.speed * self.delta_time
        
        if glfw.get_key(self.window, glfw.KEY_W) == glfw.PRESS:
            self.camera.pos += camera_speed * self.camera.front
        if glfw.get_key(self.window, glfw.KEY_S) == glfw.PRESS:
            self.camera.pos -= camera_speed * self.camera.front
        if glfw.get_key(self.window, glfw.KEY_A) == glfw.PRESS:
            self.camera.pos -= pyrr.vector3.normalize(
                pyrr.vector3.cross(self.camera.front, self.camera.up)
            ) * camera_speed
        if glfw.get_key(self.window, glfw.KEY_D) == glfw.PRESS:
            self.camera.pos += pyrr.vector3.normalize(
                pyrr.vector3.cross(self.camera.front, self.camera.up)
            ) * camera_speed
    
    def framebuffer_size_callback(self, window, width, height):
        glViewport(0, 0, width, height)
        self.width = width
        self.height = height
    
    def mouse_callback(self, window, xpos, ypos):
        if self.first_mouse:
            self.last_x = xpos
            self.last_y = ypos
            self.first_mouse = False
            
        xoffset = xpos - self.last_x
        yoffset = self.last_y - ypos  # Reversed since y-coordinates go from bottom to top
        self.last_x = xpos
        self.last_y = ypos
        
        sensitivity = 0.1
        xoffset *= sensitivity
        yoffset *= sensitivity
        
        self.camera.yaw += xoffset
        self.camera.pitch += yoffset
        
        # Make sure that when pitch is out of bounds, screen doesn't get flipped
        if self.camera.pitch > 89.0:
            self.camera.pitch = 89.0
        if self.camera.pitch < -89.0:
            self.camera.pitch = -89.0
            
        # Update front, right and up vectors using the updated Euler angles
        front = pyrr.Vector3([
            np.cos(np.radians(self.camera.yaw)) * np.cos(np.radians(self.camera.pitch)),
            np.sin(np.radians(self.camera.pitch)),
            np.sin(np.radians(self.camera.yaw)) * np.cos(np.radians(self.camera.pitch))
        ])
        self.camera.front = pyrr.vector3.normalize(front)
    
    def scroll_callback(self, window, xoffset, yoffset):
        self.camera.zoom -= yoffset
        if self.camera.zoom < 1.0:
            self.camera.zoom = 1.0
        if self.camera.zoom > 45.0:
            self.camera.zoom = 45.0
    
    def check_gl_error(self, message):
        error = glGetError()
        if error != GL_NO_ERROR:
            print(f"OpenGL Error ({message}): {error}")
            return True
        return False

    def run(self):
        if not self.shader_program:
            print("Failed to initialize shader program. Exiting...")
            glfw.terminate()
            return

        while not glfw.window_should_close(self.window):
            # Per-frame time logic
            current_frame = glfw.get_time()
            self.delta_time = current_frame - self.last_frame
            self.last_frame = current_frame
            
            # Input
            self.process_input()
            
            try:
                # Clear the screen
                glClearColor(0.1, 0.1, 0.1, 1.0)
                glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
                
                # Use shader program
                glUseProgram(self.shader_program)
                
                # Projection matrix (field of view, aspect ratio, near and far planes)
                projection = pyrr.matrix44.create_perspective_projection(
                    self.camera.zoom, 
                    self.width / self.height, 
                    0.1, 
                    100.0
                )
                glUniformMatrix4fv(self.proj_loc, 1, GL_FALSE, projection)
                
                # Camera/view transformation
                view = self.camera.get_view_matrix()
                glUniformMatrix4fv(self.view_loc, 1, GL_FALSE, view)
                
                # Bind the Vertex Array Object first, then bind and set vertex buffer(s) and attribute pointer(s)
                glBindVertexArray(self.vao)
                
                # Create model matrix (rotates the Zia)
                self.rotation += 0.5 * self.delta_time
                model = pyrr.Matrix44.identity()
                model = pyrr.matrix44.multiply(
                    model,
                    pyrr.matrix44.create_from_axis_rotation(
                        [0.5, 1.0, 0.0],
                        np.radians(self.rotation * 50)
                    )
                )
                
                glUniformMatrix4fv(self.model_loc, 1, GL_FALSE, model)
                
                # Draw the Zia
                # 6 floats per vertex (3 for position, 3 for color)
                glDrawArrays(GL_TRIANGLES, 0, len(self.vertices) // 6)
                
                # Check for OpenGL errors after draw call
                if self.check_gl_error("After draw"):
                    break
                
                # Unbind VAO (not strictly necessary but good practice)
                glBindVertexArray(0)
                
                # Swap buffers and poll IO events
                glfw.swap_buffers(self.window)
                
            except Exception as e:
                print(f"Error in main loop: {e}")
                break
                
            glfw.poll_events()
        
        # Cleanup
        try:
            glBindVertexArray(0)
            glDisableVertexAttribArray(0)
            glDisableVertexAttribArray(1)
            
            # Properly delete buffers
            if hasattr(self, 'vbo') and self.vbo is not None:
                glDeleteBuffers(1, [self.vbo])
                self.vbo = None
                
            if hasattr(self, 'vao') and self.vao is not None:
                glDeleteVertexArrays(1, [self.vao])
                self.vao = None
                
            if hasattr(self, 'shader_program') and self.shader_program is not None:
                glDeleteProgram(self.shader_program)
                self.shader_program = None
                
        except Exception as e:
            print(f"Error during cleanup: {e}")
        
        # Terminate GLFW, clearing any allocated resources
        if glfw.get_current_context() is not None:
            glfw.terminate()

def main():
    app = Zia3DModern()
    app.run()

if __name__ == "__main__":
    main()
