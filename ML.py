import numpy
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split


class ML:

    def create_model(self, audio_features, labels):

        # Train, Test, & Split

        X = numpy.array(audio_features)

        y = numpy.array(labels)

        X_train, X_test, y_train, y_test = train_test_split(X, y, train_size=0.80)

        # Create model

        clf = RandomForestClassifier()

        model = clf.fit(X_train, y_train)

        return model



