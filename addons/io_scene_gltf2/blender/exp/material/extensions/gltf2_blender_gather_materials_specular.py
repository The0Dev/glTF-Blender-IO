# Copyright 2018-2022 The glTF-Blender-IO authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import bpy
from .....io.com.gltf2_io_extensions import Extension
from ....exp import gltf2_blender_get
from ...material.gltf2_blender_gather_texture_info import gather_texture_info

def export_specular(blender_material, export_settings):
    specular_extension = {}
    extensions_needed = False

    specular_socket = gltf2_blender_get.get_socket(blender_material, 'Specular IOR Level')
    speculartint_socket = gltf2_blender_get.get_socket(blender_material, 'Specular Tint')

    if specular_socket is None or speculartint_socket is None:
        return None, {}

    uvmap_infos = {}

    specular_non_linked = isinstance(specular_socket, bpy.types.NodeSocket) and not specular_socket.is_linked
    specularcolor_non_linked = isinstance(speculartint_socket, bpy.types.NodeSocket) and not speculartint_socket.is_linked

    if specular_non_linked is True:
        fac = specular_socket.default_value
        fac = fac * 2.0
        if fac < 1.0:
            specular_extension['specularFactor'] = fac
            extensions_needed = True
        elif fac > 1.0:
            # glTF specularFactor should be <= 1.0, so we will multiply ColorFactory by specularFactor, and set SpecularFactor to 1.0 (default value)
            extensions_needed = True
        else:
            pass # If fac == 1.0, no need to export specularFactor, the default value is 1.0

    else:
        # Factor
        fac = gltf2_blender_get.get_factor_from_socket(specular_socket, kind='VALUE')
        if fac is not None and fac != 1.0:
            fac = fac * 2.0 if fac is not None else None
            if fac is not None and fac < 1.0:
                specular_extension['specularFactor'] = fac
                extensions_needed = True
            elif fac is not None and fac > 1.0:
                # glTF specularFactor should be <= 1.0, so we will multiply ColorFactory by specularFactor, and set SpecularFactor to 1.0 (default value)
                extensions_needed = True

        # Texture
        if gltf2_blender_get.has_image_node_from_socket(specular_socket):
            original_specular_texture, uvmap_info, _ = gather_texture_info(
                specular_socket,
                (specular_socket,),
                (),
                export_settings,
            )
            specular_extension['specularTexture'] = original_specular_texture
            uvmap_infos.update({'specularTexture': uvmap_info})
            extensions_needed = True

    if specularcolor_non_linked is True:
        color = speculartint_socket.default_value[:3]
        if fac is not None and fac > 1.0:
            color = (color[0] * fac, color[1] * fac, color[2] * fac)
        specular_extension['specularColorFactor'] = color if color != (1.0, 1.0, 1.0) else None
        if color != (1.0, 1.0, 1.0):
            extensions_needed = True

    else:
        # Factor
        fac_color = gltf2_blender_get.get_factor_from_socket(speculartint_socket, kind='RGB')
        if fac_color is not None and fac is not None and fac > 1.0:
            fac_color = (fac_color[0] * fac, fac_color[1] * fac, fac_color[2] * fac)
        elif fac_color is None and fac is not None and fac > 1.0:
            fac_color = (fac, fac, fac)
        specular_extension['specularColorFactor'] = fac_color if fac_color != (1.0, 1.0, 1.0) else None
        if fac_color != (1.0, 1.0, 1.0):
            extensions_needed = True

        # Texture
        if gltf2_blender_get.has_image_node_from_socket(speculartint_socket):
            original_specularcolor_texture, uvmap_info, _ = gather_texture_info(
                speculartint_socket,
                (speculartint_socket,),
                (),
                export_settings,
            )
            specular_extension['specularColorTexture'] = original_specularcolor_texture
            uvmap_infos.update({'specularColorTexture': uvmap_info})
            extensions_needed = True

    if extensions_needed is False:
        return None, {}

    return Extension('KHR_materials_specular', specular_extension, False), uvmap_infos
