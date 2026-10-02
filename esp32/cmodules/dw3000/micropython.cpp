#include "py/runtime.h"
#include "py/obj.h"
#include "dw3000_wrapper.h"

STATIC mp_obj_t py_dw3000_init(size_t n_args, const mp_obj_t *args) {
    return mp_obj_new_int(dw3000_init_c(mp_obj_get_int(args[0]), mp_obj_get_int(args[1]), mp_obj_get_int(args[2])));
}
STATIC MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(py_dw3000_init_obj, 3, 3, py_dw3000_init);

STATIC mp_obj_t py_dw3000_read_distance(void) {
    return mp_obj_new_float(dw3000_read_distance_c());
}
STATIC MP_DEFINE_CONST_FUN_OBJ_0(py_dw3000_read_distance_obj, py_dw3000_read_distance);

STATIC const mp_rom_map_elem_t dw3000_globals_table[] = {
    { MP_ROM_QSTR(MP_QSTR___name__), MP_ROM_QSTR(MP_QSTR_dw3000) },
    { MP_ROM_QSTR(MP_QSTR_init), MP_ROM_PTR(&py_dw3000_init_obj) },
    { MP_ROM_QSTR(MP_QSTR_read_distance), MP_ROM_PTR(&py_dw3000_read_distance_obj) },
};
STATIC MP_DEFINE_CONST_DICT(dw3000_globals, dw3000_globals_table);

const mp_obj_module_t dw3000_user_cmodule = {
    .base = { &mp_type_module },
    .globals = (mp_obj_dict_t *)&dw3000_globals,
};
MP_REGISTER_MODULE(MP_QSTR_dw3000, dw3000_user_cmodule);
