define([
    "dojo/_base/declare",
    "dojo/_base/array",
    "dojo/_base/lang",
    "dojo/request/xhr",
    "dojo/store/Memory",
    "dojo/data/ObjectStore",
    "dijit/_TemplatedMixin",
    "dijit/_WidgetsInTemplateMixin",
    "dijit/layout/ContentPane",
    "ngw-pyramid/i18n!rosreestr",
    "ngw-pyramid/hbs-i18n",
    "ngw-resource/serialize",
    "ngw/route",
    // resource
    "dojo/text!./template/Widget.hbs",
    // template
    "dijit/form/ComboBox",
    "dijit/form/CheckBox",
    "dijit/form/Select",
    "dojox/layout/TableContainer",
    "ngw-file-upload/Uploader"
], function (
    declare,
    array,
    lang,
    xhr,
    Memory,
    ObjectStore,
    _TemplatedMixin,
    _WidgetsInTemplateMixin,
    ContentPane,
    i18n,
    hbsI18n,
    serialize,
    route,
    template
) {
    var SRS_URL = route.spatial_ref_sys.collection();

    return declare([ContentPane, serialize.Mixin, _TemplatedMixin, _WidgetsInTemplateMixin], {
        templateString: hbsI18n(template, i18n),
        title: i18n.gettext("Rosreestr"),
        prefix: "rosreestr",

        postCreate: function () {
            this.inherited(arguments);

            this.wParcel.on("update", lang.hitch(this, this.populateResource));
            this.wOKSPolygon.on("update", lang.hitch(this, this.populateResource));
            this.wOKSLinear.on("update", lang.hitch(this, this.populateResource));
            this.wOKSPoint.on("update", lang.hitch(this, this.populateResource));
            this.wSpatialData.on("update", lang.hitch(this, this.populateResource));
            this.wBound.on("update", lang.hitch(this, this.populateResource));
            this.wBoundLinear.on("update", lang.hitch(this, this.populateResource));
            this.wOMS.on("update", lang.hitch(this, this.populateResource));
            this.wZone.on("update", lang.hitch(this, this.populateResource));
        },

        startup: function () {
            this.inherited(arguments);

            xhr.get(SRS_URL, {
                handleAs: 'json'
            }).then(lang.hitch(this, function (data) {
                this.wSRS.set('store', new ObjectStore(new Memory({
                    data: array.map(data, function (item) {
                        return {
                            id: item.id,
                            label: item.display_name
                        }
                    })
                })));
            }));
        },

        populateResource: function (e) {
            var res = e.value, targetWidget = e.detail.widget.dojoAttachPoint + 'Attr';
            xhr.get(route.feature_layer.field(res), { handleAs: "json"})
                .then(lang.hitch(this, function (response) {
                    var res_col = [];
                    array.forEach(response, function (item) {
                        res_col.push({id: item.keyname, label: item.display_name})
                    }, this);
                    this[targetWidget].set("store", new Memory({
                        data: res_col
                    }));
                    var that = this;
                    xhr.get(route.feature_layer.inspect(res), { handleAs: "json"})
                        .then(
                            function (response) {
                                that[targetWidget].set("value", response.keyname);
                            },
                            function (err) {
                                console.log(err);
                            });
                }));
        },

        serializeInMixin: function (data) {
            var prefix = this.prefix,
                setObject = function (key, value) { lang.setObject(prefix + "." + key, value, data); };

            setObject("srs", this.wSRS.get("value"));
            setObject("source", this.wSourceFile.get("value"));
            setObject("update", this.wUpdate.get("value"));
        },

        validateDataInMixin: function (errback) {
            return this.wSourceFile.upload_promise !== undefined && this.wSourceFile.upload_promise.isResolved();
        }
    });
});
