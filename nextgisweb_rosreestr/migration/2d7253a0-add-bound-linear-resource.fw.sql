/*** {
    "revision": "2d7253a0", "parents": ["00000000"],
    "date": "2021-03-19T11:44:10",
    "message": "add bound linear resource"
} ***/

-- TODO: Write code here and remove this placeholder line!
ALTER TABLE rosreestr ADD COLUMN bound_linear_resource_id int4 NULL;
ALTER TABLE rosreestr ADD CONSTRAINT rosreestr_linear_bound_resource_id_fkey FOREIGN KEY (bound_linear_resource_id) REFERENCES resource(id);