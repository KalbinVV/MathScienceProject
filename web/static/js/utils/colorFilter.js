function makeFilter(minValue, maxValue, className, color, name) {
    return {
        inRange: function(currentValue) {
            return true ? currentValue > minValue && currentValue < maxValue : false
        },

        getClassName: function() {
            return className
        },

        getColor: function() {
            return color
        },

        getName: function() {
            return name
        }
    }
}

function getFilter(filterCode) {
    return {
        strong: makeFilter(0.7, 1, 'strong_binding', 'blue', 'strong'),
        average: makeFilter(0.5, 0.7, 'average_binding', '#006600', 'average'),
        moderate: makeFilter(0.3, 0.5, 'moderate_binding', '#00cc00', 'moderate'),
        weak: makeFilter(0.2, 0.3, 'weak_binding', '#cc0000', 'weak', 'weak'),
        very_weak: makeFilter(0, 0.2, 'very_weak_binding', '#800000', 'very_weak')
    }[filterCode]
}